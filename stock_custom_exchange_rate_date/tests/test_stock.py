from datetime import timedelta

from odoo import fields
from odoo.tests import Form, TransactionCase


class TestStock(TransactionCase):
    def setUp(self):
        super().setUp()
        self.vendor = self.env.ref('base.res_partner_1')
        self.usd = self.env.ref('base.USD')
        self.eur = self.env.ref('base.EUR')
        self.today = fields.Date.context_today(self.env.user)
        self.yesterday = self.today - timedelta(days=1)
        self.set_currency_rates(self.today, usd_rate=1, eur_rate=1.25)
        self.set_currency_rates(self.yesterday, usd_rate=1, eur_rate=2)
        self.env.user.company_id.currency_id = self.usd

        # Creating a new product to ensure valuation is clean
        self.product = self.env['product.product'].create({
            'name': 'Product fifo',
            'type': 'product',
            'default_code': 'PR-FIFO',
            'valuation': 'real_time',
            'cost_method': 'fifo',
        })

    def create_purchase_order(self, partner=None, **line_kwargs):
        if partner is None:
            partner = self.vendor
        purchase_order = Form(self.env['purchase.order'])
        purchase_order.partner_id = partner
        purchase_order.currency_id = self.eur
        purchase_order = purchase_order.save()
        self.create_po_line(purchase_order, **line_kwargs)
        return purchase_order

    def create_po_line(self, purchase_order, product=None, quantity=1, price=100):
        if product is None:
            product = self.product
        with Form(purchase_order) as po:
            with po.order_line.new() as line:
                line.product_id = product
                line.product_qty = quantity
                line.price_unit = price

    def process_immediate_transfer(self, picking):
        immediate_transfer = self.env['stock.immediate.transfer'].create({
            'pick_ids': [(6, 0, picking.ids)],
        })
        return immediate_transfer.process()

    def set_currency_rates(self, rate_date, usd_rate, eur_rate):
        # Remove existing rates, if any
        rate_model = self.env['res.currency.rate']
        current_rates = rate_model.search([
            ('name', '=', rate_date),
            ('currency_id', 'in', [self.usd.id, self.eur.id]),
        ])
        current_rates.unlink()

        # Create new rates
        rate_model.create({
            'currency_id': self.usd.id,
            'rate': usd_rate,
            'name': rate_date,
        })
        rate_model.create({
            'currency_id': self.eur.id,
            'rate': eur_rate,
            'name': rate_date
        })

    def test_01_date_rate_set(self):
        """Set a custom rate date on a transfer, valuation should be computed using that date"""
        # Purchase product
        po = self.create_purchase_order()
        po.button_confirm()
        self.assertEqual(po.state, 'purchase')
        self.assertEqual(po.picking_count, 1)

        # Set custom rate date on the receipt transfer and confirm
        picking_po = po.picking_ids
        picking_po.exchange_rate_date = self.yesterday
        self.process_immediate_transfer(picking_po)
        self.assertEqual(picking_po.state, 'done')

        # Check valuation according to stock moves
        # Yesterday's rate was 1 USD = 2 EUR, so 100 EUR should be valued as 50 USD
        self.assertRecordValues(picking_po.move_lines, [{
            'remaining_qty': 1.0,
            'remaining_value': 50.0,
            'value': 50.0,
        }])

        # Check valuation according to journal entries
        self.assertEqual(self.product.stock_value, 50.0)
        self.assertRecordValues(self.product.stock_fifo_real_time_aml_ids, [{
            'debit': 50.0,
            'credit': 0.0,
            'amount_currency': 100.0,
            'currency_id': self.eur.id,
            'account_id': self.product.categ_id.property_stock_valuation_account_id.id,
        }])

    def test_02_date_rate_not_set(self):
        """Don't set a custom date rate, valuation should be computed using today"""
        # Purchase product
        po = self.create_purchase_order()
        po.button_confirm()
        self.assertEqual(po.state, 'purchase')
        self.assertEqual(po.picking_count, 1)

        # Confirm receipt transfer
        picking_po = po.picking_ids
        self.process_immediate_transfer(picking_po)
        self.assertEqual(picking_po.state, 'done')

        # Check valuation according to stock moves
        # Today's rate is 1 USD = 1.25 EUR, so 100 EUR should be valued as 80 USD
        self.assertRecordValues(picking_po.move_lines, [{
            'remaining_qty': 1.0,
            'remaining_value': 80.0,
            'value': 80.0,
        }])

        # Check valuation according to journal entries
        self.assertEqual(self.product.stock_value, 80.0)
        self.assertRecordValues(self.product.stock_fifo_real_time_aml_ids, [{
            'debit': 80.0,
            'credit': 0.0,
            'amount_currency': 100.0,
            'currency_id': self.eur.id,
            'account_id': self.product.categ_id.property_stock_valuation_account_id.id,
        }])
