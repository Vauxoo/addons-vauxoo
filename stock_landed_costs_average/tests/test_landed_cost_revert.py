# -*- coding: utf-8 -*-

from openerp.tests.common import TransactionCase
from datetime import datetime, timedelta


class TestLandedCostRevert(TransactionCase):

    def setUp(self):
        super(TestLandedCostRevert, self).setUp()
        self.company_id = self.env.ref('base.main_company')
        self.slc = self.env['stock.landed.cost']
        self.slc_id = self.env.ref('stock_landed_costs_average.slc_02')
        self.delta = 0
        self.next_hour = datetime.strptime('2016-01-01 01:00:00',
                                           '%Y-%m-%d %H:%M:%S')
        self.product_freight_id = self.env.ref(
            'stock_landed_costs_average'
            '.service_standard_periodic_landed_cost_1')
        self.account_freight_id = self.env.ref(
            'stock_landed_costs_average.freight_account')
        self.picking = self.env['stock.picking']
        self.move = self.env['stock.move']
        self.purchase_order = self.env['purchase.order']
        self.sale_order = self.env['sale.order']
        self.product_id = self.env.ref(
            'stock_landed_costs_average.product_mouse')
        self.wizard = self.env['stock.transfer_details']
        self.wizard_item = self.env['stock.transfer_details_items']
        self.transfer_details = self.env['stock.transfer_details']
        self.supplier_id = self.env.ref('base.res_partner_13')
        self.customer_id = self.env.ref('base.res_partner_23')
        self.transactions = [
            {
                'cost': 20, 'qty': 2,
                'avg': 20, 'is_po': True,
            },
            {
                'cost': 40, 'qty': 3,
                'avg': 32, 'is_po': True,
            },
            {
                'cost': 32, 'qty': 1,
                'avg': 32, 'is_po': False,
            },
            {
                'cost': 64, 'qty': 4,
                'avg': 48, 'is_po': True,
            },
            {
                'cost': 48, 'qty': 4,
                'avg': 48, 'is_po': False,
            },
        ]
        self.expected_values = {
            self.ref('account.stk'): {
                'credit': [40, 24],
                'debit': [40, 24],
            },
            self.ref('account.a_expense'): {
                'credit': [24],
                'debit': [24],
            },
            self.account_freight_id.id: {
                'credit': [40],
                'debit': [40],
            },
        }

    def dummy_function(self, move_lines):
        for move_id in move_lines:
            self.delta += 1
            self.next_hour = datetime.strptime(
                '2016-01-01 01:00:00',
                '%Y-%m-%d %H:%M:%S') + timedelta(hours=self.delta)
            move_id.write({'date': self.next_hour})

    def do_picking_wf(self, picking_id):
        picking_id.action_confirm()
        wizard_id = self.wizard.create({
            'picking_id': picking_id.id,
        })

        for move_id in picking_id.move_lines:
            self.wizard_item.create({
                'transfer_id': wizard_id.id,
                'product_id': move_id.product_id.id,
                'quantity': move_id.product_qty,
                'sourceloc_id': move_id.location_id.id,
                'destinationloc_id': move_id.location_dest_id.id,
                'product_uom_id': move_id.product_uom.id,
            })

        wizard_id.do_detailed_transfer()

    def do_picking(self, picking_ids):
        if not picking_ids:
            return

        for picking_id in picking_ids:
            self.do_picking_wf(picking_id)
            self.assertEqual(picking_id.state, 'done')
            self.dummy_function(picking_id.move_lines)

    def create_purchase_order(self, vals):
        qty = vals['qty']
        cost = vals['cost']
        purchase_order_id = self.purchase_order.create({
            'partner_id': self.supplier_id.id,
            'location_id': self.ref('stock.stock_location_stock'),
            'pricelist_id': self.ref('purchase.list0'),
            'order_line': [(0, 0, {
                'name': "{0} (qty={1}, cost={2})".format(self.product_id.name,
                                                         qty, cost),
                'product_id': self.product_id.id,
                'price_unit': cost,
                'product_qty': qty,
                'date_planned': datetime.now().strftime('%Y-%m-%d'),
            })]
        })

        purchase_order_id.wkf_confirm_order()
        purchase_order_id.action_invoice_create()
        purchase_order_id.action_picking_create()
        self.do_picking(purchase_order_id.picking_ids)
        return purchase_order_id

    def create_sale_order(self, vals):
        qty = vals['qty']
        price = vals['cost']
        sale_order_id = self.sale_order.create({
            'partner_id': self.customer_id.id,
            'client_order_ref': "Sale Order (qty={0}, price={1})".format(
                str(qty), str(price)),
            'order_policy': 'manual',
            'order_line': [(0, 0, {
                'product_id': self.product_id.id,
                'product_uom_qty': qty,
                'price_unit': price,
            })]
        })

        sale_order_id.action_button_confirm()
        self.do_picking(sale_order_id.picking_ids)
        return sale_order_id

    def get_stock_card_lines(self, product_id):
        return self.env['stock.card.product'].\
            _stock_card_move_get(product_id)['res']

    def create_and_validate_landed_costs(self, picking_id):
        slc_id = self.slc.create({
            'account_journal_id': self.ref(
                'stock_landed_costs_average.stock_landed_cost_1'),
            'picking_ids': [(4, picking_id.id), ],
            'cost_lines': [
                (0, 0, {
                    'name': 'freight',
                    'product_id': self.product_freight_id.id,
                    'account_id': self.account_freight_id.id,
                    'split_method': 'by_quantity',
                    'price_unit': 40,
                }),
            ]
        })
        self.assertEqual(len(slc_id.picking_ids), 1)
        self.assertEqual(len(slc_id.cost_lines), 1)
        slc_id.compute_landed_cost()
        self.assertEqual(len(slc_id.valuation_adjustment_lines), 1)
        slc_id.button_validate()

        return slc_id

    def revert_landed_cost(self, landed_cost_id):
        reverted_lc_id = landed_cost_id.copy()
        reverted_lc_id.write({
            'picking_ids': [(6, 0, landed_cost_id.picking_ids.mapped('id'))],
        })

        for line in reverted_lc_id.cost_lines:
            line.write({
                'price_unit': -1 * line.price_unit
            })
        reverted_lc_id.compute_landed_cost()
        reverted_lc_id.button_validate()
        return reverted_lc_id

    def test_01_landed_cost_revert(self):
        card_lines = {}
        for trx in self.transactions:
            # purchase
            if trx['is_po']:
                trx['id'] = self.create_purchase_order(trx)
            else:  # sale
                trx['id'] = self.create_sale_order(trx)
            trx['picking_ids'] = trx['id'].picking_ids

        card_lines['before_landed'] = self.get_stock_card_lines(
            self.product_id.id)
        picking_id = self.transactions[0]['picking_ids']

        landed_cost_id = self.create_and_validate_landed_costs(picking_id)
        self.validate_acct_entries_values(
            landed_cost_id, self.product_id,  self.expected_values)

        card_lines['after_landed'] = self.get_stock_card_lines(
            self.product_id.id)

        revert_landed_cost_id = self.revert_landed_cost(landed_cost_id)
        self.validate_acct_entries_values(
            revert_landed_cost_id, self.product_id, self.expected_values)

        card_lines['after_revert'] = self.get_stock_card_lines(
            self.product_id.id)

        # check for values before applying landed cost and after revert landed
        # cost are the same
        self.assertEqual(
            card_lines['before_landed'], card_lines['after_revert'],
            'Something is not right with before_landed={0} '
            'and after_revert={1}'.format(card_lines['before_landed'],
                                          card_lines['after_revert']))

    def validate_acct_entries_values(self, landed_cost_id, product_id, vals):
        acct_move_id = landed_cost_id.account_move_id
        self.assertEqual(acct_move_id.mapped('line_id.product_id'), product_id)
        for aml_id in acct_move_id.line_id:
            acct_id = aml_id.account_id.id
            debit = aml_id.debit
            credit = aml_id.credit

            # check values expected for credit and debit
            self.assertTrue(
                credit and credit in vals[acct_id]['credit'] or
                debit and debit in vals[acct_id]['debit'])
