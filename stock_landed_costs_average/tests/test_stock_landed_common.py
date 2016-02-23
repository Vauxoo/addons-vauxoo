# -*- coding: utf-8 -*-

from openerp.tests.common import TransactionCase
from datetime import datetime, timedelta
from openerp.tools.safe_eval import safe_eval


class TestStockLandedCommon(TransactionCase):

    def setUp(self):
        super(TestStockLandedCommon, self).setUp()
        self.slc = self.env['stock.landed.cost']
        self.picking = self.env['stock.picking']
        self.move = self.env['stock.move']
        self.purchase_order = self.env['purchase.order']
        self.sale_order = self.env['sale.order']
        self.wizard = self.env['stock.transfer_details']
        self.wizard_item = self.env['stock.transfer_details_items']
        self.transfer_details = self.env['stock.transfer_details']
        self.return_picking = self.env['stock.return.picking']
        self.return_picking_line = self.env['stock.return.picking.line']
        self.delta = 0
        self.next_hour = datetime.strptime('2016-01-01 01:00:00',
                                           '%Y-%m-%d %H:%M:%S')

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

    def create_return(self, vals):
        qty = vals['qty']
        picking_id = vals['origin_id']
        return_id = self.return_picking.with_context({
            'active_id': picking_id.id,
            'active_ids': picking_id.ids,
            'active_model': 'stock.picking',
        }).create({})

        return_lines = []
        for move_id in picking_id.move_lines:
            return_line_id = self.return_picking_line.create({
                'product_id': self.product_id.id,
                'quantity': qty,
                'wizard_id': return_id.id,
                'move_id': move_id.id
            })
            return_lines.append(return_line_id)
        res = return_id.create_returns()
        picking_id = safe_eval(res['domain'])[0][2][0]
        picking_id = self.picking.browse(picking_id)
        self.do_picking_wf(picking_id)
        self.assertEqual(picking_id.state, 'done')
        self.dummy_function(picking_id.move_lines)
        return picking_id.id

    def get_stock_card_lines(self, product_id):
        return self.env['stock.card.product'].\
            _stock_card_move_get(product_id)['res']

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
