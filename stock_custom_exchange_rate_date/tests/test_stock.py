from datetime import timedelta

from odoo import fields
from odoo.tests import Form, TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestStock(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.vendor = cls.env.ref("base.res_partner_1")
        cls.usd = cls.env.ref("base.USD")
        cls.eur = cls.env.ref("base.EUR")
        cls.today = fields.Date.context_today(cls.env.user)
        cls.yesterday = cls.today - timedelta(days=1)
        account = cls.env["account.account"].create(
            {
                "name": "Receivable",
                "code": "RCV00",
                "account_type": "asset_receivable",
                "reconcile": True,
            }
        )
        account_expense = cls.env["account.account"].create(
            {
                "name": "Expense",
                "code": "EXP00",
                "account_type": "expense",
                "reconcile": True,
            }
        )
        account_income = cls.env["account.account"].create(
            {
                "name": "Income",
                "code": "INC00",
                "account_type": "income",
                "reconcile": True,
            }
        )
        account_output = cls.env["account.account"].create(
            {
                "name": "Output",
                "code": "OUT00",
                "account_type": "expense",
                "reconcile": True,
            }
        )
        account_valuation = cls.env["account.account"].create(
            {
                "name": "Valuation",
                "code": "STV00",
                "account_type": "expense",
                "reconcile": True,
            }
        )
        stock_journal = cls.env["account.journal"].create(
            {
                "name": "Stock journal",
                "type": "sale",
                "code": "STK00",
            }
        )

        # Creating a new product to ensure valuation is clean
        cls.stock_account_product_categ = cls.env["product.category"].create(
            {
                "name": "Test category",
                "property_valuation": "real_time",
                "property_cost_method": "fifo",
                "property_account_income_categ_id": account_income.id,
                "property_account_expense_categ_id": account_expense.id,
                "property_stock_account_input_categ_id": account.id,
                "property_stock_account_output_categ_id": account_output.id,
                "property_stock_valuation_account_id": account_valuation.id,
                "property_stock_journal": stock_journal.id,
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product fifo",
                "type": "product",
                "default_code": "PR-FIFO",
                "categ_id": cls.stock_account_product_categ.id,
            }
        )

    def create_purchase_order(self, partner=None, **line_kwargs):
        if partner is None:
            partner = self.vendor
        purchase_order = Form(self.env["purchase.order"])
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

    def set_currency_rates(self, rate_date, usd_rate, eur_rate):
        # Remove existing rates, if any
        rate_model = self.env["res.currency.rate"]
        current_rates = rate_model.search(
            [
                ("name", "=", rate_date),
                ("currency_id", "in", [self.usd.id, self.eur.id]),
            ]
        )
        current_rates.unlink()

        # Create new rates
        rate_model.create(
            {
                "currency_id": self.usd.id,
                "rate": usd_rate,
                "name": rate_date,
            }
        )
        rate_model.create({"currency_id": self.eur.id, "rate": eur_rate, "name": rate_date})

    def test_01_date_rate_set(self):
        """Set a custom rate date on a transfer, valuation should be computed using that date"""
        # Purchase product
        self.set_currency_rates(rate_date=self.today, usd_rate=1, eur_rate=1.25)
        self.set_currency_rates(rate_date=self.yesterday, usd_rate=1, eur_rate=2)
        po = self.create_purchase_order()
        po.button_confirm()
        self.assertEqual(po.state, "purchase")

        # Set custom rate date on the receipt transfer and confirm
        picking_po = po.picking_ids
        picking_po.exchange_rate_date = self.yesterday
        picking_po.move_line_ids.write({"qty_done": 1.0})
        picking_po.button_validate()
        self.assertEqual(picking_po.state, "done")

        # Check valuation according to stock moves
        # Yesterday's rate was 1 USD = 2 EUR, so 100 EUR should be valued as 50 USD
        val_layer = self.env["stock.valuation.layer"].search([("stock_move_id", "in", picking_po.move_ids.ids)])
        self.assertRecordValues(
            val_layer,
            [
                {
                    "remaining_qty": 1.0,
                    "remaining_value": 50.0,
                    "value": 50.0,
                }
            ],
        )

    def test_02_date_rate_not_set(self):
        """Don't set a custom date rate, valuation should be computed using today"""
        # Purchase product
        self.set_currency_rates(rate_date=self.today, usd_rate=1, eur_rate=1.25)
        self.set_currency_rates(rate_date=self.yesterday, usd_rate=1, eur_rate=2)
        po = self.create_purchase_order()
        po.button_confirm()
        self.assertEqual(po.state, "purchase")

        # Confirm receipt transfer
        picking_po = po.picking_ids
        picking_po.move_line_ids.write({"qty_done": 1.0})
        picking_po.button_validate()
        self.assertEqual(picking_po.state, "done")

        # Check valuation according to stock moves
        # Today"s rate is 1 USD = 1.25 EUR, so 100 EUR should be valued as 80 USD
        val_layer = self.env["stock.valuation.layer"].search([("stock_move_id", "in", picking_po.move_ids.ids)])
        self.assertRecordValues(
            val_layer,
            [
                {
                    "remaining_qty": 1.0,
                    "remaining_value": 80.0,
                    "value": 80.0,
                }
            ],
        )
