# -*- coding: utf-8 -*-

from openerp.tests.common import TransactionCase
from openerp.exceptions import except_orm, Warning as UserError
from datetime import datetime, timedelta
from openerp.tools.safe_eval import safe_eval


class TestLandedCostAverage(TransactionCase):

    def setUp(self):
        super(TestLandedCostAverage, self).setUp()
        self.company_id = self.env.ref('base.main_company')
        self.slc = self.env['stock.landed.cost']
        self.slc_id = self.env.ref('stock_landed_costs_average.slc_02')
        self.delta = 0
        self.next_hour = datetime.strptime('2016-01-01 01:00:00',
                                           '%Y-%m-%d %H:%M:%S')
        self.picking = self.env['stock.picking']
        self.move = self.env['stock.move']
        self.customer_location = self.env.ref('stock.stock_location_customers')
        self.supplier_location = self.env.ref('stock.stock_location_suppliers')
        self.stock_location = self.env.ref('stock.stock_location_stock')
        self.supplier_id = self.env.ref('base.res_partner_13')
        self.customer_id = self.env.ref('base.res_partner_23')
        self.purchase_order = self.env['purchase.order']
        self.sale_order = self.env['sale.order']
        self.product_id = self.env.ref(
            'stock_landed_costs_average.product_mouse')
        self.wizard = self.env['stock.transfer_details']
        self.wizard_item = self.env['stock.transfer_details_items']
        self.transfer_details = self.env['stock.transfer_details']
        self.return_picking = self.env['stock.return.picking']
        self.return_picking_line = self.env['stock.return.picking.line']
        self.transactions = [
            {  # 1 buy 8 items
                'name': 'slca_po_01',
                'is_po': True, 'is_return': False, 'cost': 10, 'qty': 8,
                'avg': 10, 'move_val': 80, 'inv_val': 80,
            },
            {  # 2 buy 4 items
                'name': 'slca_po_02',
                'is_po': True, 'is_return': False, 'cost': 16, 'qty': 4,
                'avg': 20, 'move_val': 40, 'inv_val': 40,
            },
            {  # 3 sale 10 items
                'name': 'slca_so_01',
                'is_po': False, 'is_return': False, 'cost': 12, 'qty': 10,
                'avg': 12, 'move_val': 120, 'inv_val': 24,
            },
            {  # 4 sale 1 item
                'name': 'slca_so_02',
                'is_po': False, 'is_return': False, 'cost': 12, 'qty': 1,
                'avg': 12, 'move_val': 12, 'inv_val': 12,
                'origin_name': 'po_01',
            },
            {  # 5 vendor return 1 item
                'name': 'slca_ret_po_01',
                'is_po': True, 'is_return': True, 'cost': 12, 'qty': 1,
                'avg': 12, 'move_val': 12, 'inv_val': 0,
                'origin_name': 'slca_po_01', 'partner_id': self.supplier_id,
            },
        ]

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

    def get_locations(self, is_po, is_return):

        if is_po and not is_return:
            return self.supplier_location.id, self.stock_location.id
        if is_po and is_return:
            return self.stock_location.id, self.supplier_location.id
        if not is_po and not is_return:
            return self.stock_location.id, self.customer_location.id
        if not is_po and is_return:
            return self.customer_location.id, self.stock_location.id

    def get_origin_picking(self, origin_name):
        for trx in self.transactions:
            if trx['name'] == origin_name:
                return trx['id'].picking_ids
        return False

    def create_return(self, vals):
        qty = vals['qty']
        location_id, location_dest_id = self.get_locations(vals['is_po'],
                                                           vals['is_return'])
        for picking_id in vals['origin_id']:
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

    def test_01_do_transactions(self):
        for trx in self.transactions:
            # purchase
            if trx['is_po'] and not trx['is_return']:
                trx['id'] = self.create_purchase_order(trx)

            # vendor return
            if trx['is_po'] and trx['is_return']:
                trx['origin_id'] = self.get_origin_picking(trx['origin_name'])
                trx['id'] = self.create_return(trx)

            # sale
            if not trx['is_po'] and not trx['is_return']:
                trx['id'] = self.create_sale_order(trx)
        card_lines = self.env['stock.card.product'].\
            _stock_card_move_get(self.product_id.id)['res']
        last_item = card_lines[-1]
        self.assertEqual(last_item['product_qty'], 0)
        self.assertEqual(last_item['inventory_valuation'], 0)
