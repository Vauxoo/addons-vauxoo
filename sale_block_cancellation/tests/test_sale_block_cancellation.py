# coding: utf-8
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2016 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: Luis Torres <luis_t@vauxoo.com>
#    planned by: Sabrina Romero <sabrina@vauxoo.com>
############################################################################
from openerp.tests.common import TransactionCase
from openerp.exceptions import ValidationError
from openerp.tools.safe_eval import safe_eval


class TestSaleBlockCancellation(TransactionCase):

    def setUp(self):
        super(TestSaleBlockCancellation, self).setUp()
        self.wiz_obj = self.env['stock.transfer_details']
        self.wiz_ret_obj = self.env['stock.return.picking']
        self.return_picking_line = self.env['stock.return.picking.line']
        self.proc_obj = self.env['procurement.order.compute.all']
        self.w_upd_obj = self.env['stock.change.product.qty']
        self.pick_obj = self.env['stock.picking']

        self.sale_demo = self.env.ref('sale.sale_order_1')
        self.stock_loc = self.env.ref('stock.stock_location_stock')

        self.sale_demo.warehouse_id.write({
            'delivery_steps': 'pick_pack_ship',
        })
        for line in self.sale_demo.order_line:
            self.w_upd_obj.create({
                'product_id': line.product_id.id,
                'location_id': self.stock_loc.id,
                'new_quantity': abs(
                    line.product_id.virtual_available) + line.product_uom_qty,
            }).change_product_qty()
        self.msg_error = "All the pickings are in 'Ready to transfer'"

    def test_01_allow_cancel(self):
        'Test that allow cancel Sale Order'
        sale = self.sale_demo.copy({'order_policy': 'picking'})
        sale.action_button_confirm()
        sale.action_cancel_allow()
        self.assertEquals(sale.state, 'cancel', 'Sale not cancelled')

    def test_02_no_allow_cancel_by_state(self):
        'Test that not allow cancel Sale Order, by pickings in done'
        sale = self.sale_demo.copy({'order_policy': 'picking'})
        sale.action_button_confirm()
        sale.procurement_group_id.procurement_ids.run_scheduler(False)
        sale.picking_ids.rereserve_pick()
        for picking in sale.picking_ids:
            if picking.state != 'assigned':
                continue
            wiz = self.wiz_obj.with_context({
                'active_id': picking.id,
                'active_ids': [picking.id],
                'active_model': 'stock.picking'
            }).create({'picking_id': picking.id})
            wiz.do_detailed_transfer()
            break
        with self.assertRaisesRegexp(ValidationError, self.msg_error):
            sale.action_cancel_allow()
        self.assertNotEquals(sale.state, 'cancel', 'Sale was cancelled')

    def test_03_allow_cancel_correctly_returned(self):
        'Test that allow cancel Sale Order, with pickings returned'
        sale = self.sale_demo.copy({'order_policy': 'picking'})
        sale.action_button_confirm()
        sale.procurement_group_id.procurement_ids.run_scheduler(False)
        sale.picking_ids.rereserve_pick()
        for picking in sale.picking_ids:
            if picking.state != 'assigned':
                continue
            wiz = self.wiz_obj.with_context({
                'active_id': picking.id,
                'active_ids': [picking.id],
                'active_model': 'stock.picking'
            }).create({'picking_id': picking.id})
            wiz.do_detailed_transfer()
            break
        with self.assertRaisesRegexp(ValidationError, self.msg_error):
            sale.action_cancel_allow()
        for picking in sale.picking_ids:
            if picking.state != 'done':
                continue
            return_id = self.wiz_ret_obj.with_context({
                'active_id': picking.id,
                'active_ids': picking.ids,
                'active_model': 'stock.picking'}).create({})
            nw_pick = return_id.create_returns()
            picking_id = safe_eval(nw_pick['domain'])[0][2][0]
            wiz = self.wiz_obj.with_context({
                'active_id': picking_id,
                'active_ids': [picking_id],
                'active_model': 'stock.picking'
            }).create({'picking_id': picking_id})
            wiz.do_detailed_transfer()
            break
        sale.action_cancel_allow()
        self.assertEquals(sale.state, 'cancel', 'Sale not cancelled')

    def test_04_partial_return(self):
        'Test to check that partial return not allow cancel'
        sale = self.sale_demo.copy({'order_policy': 'picking'})
        sale.order_line.write({'product_uom_qty': 10.0})
        sale.action_button_confirm()
        for line in self.sale_demo.order_line:
            self.w_upd_obj.create({
                'product_id': line.product_id.id,
                'location_id': self.stock_loc.id,
                'new_quantity': abs(
                    line.product_id.virtual_available) + line.product_uom_qty,
            }).change_product_qty()
        sale.procurement_group_id.procurement_ids.run_scheduler(False)
        sale.picking_ids.rereserve_pick()
        for picking in sale.picking_ids:
            if picking.state != 'assigned':
                continue
            wiz = self.wiz_obj.with_context({
                'active_id': picking.id,
                'active_ids': [picking.id],
                'active_model': 'stock.picking'
            }).create({'picking_id': picking.id})
            wiz.do_detailed_transfer()
            break
        for picking in sale.picking_ids:
            if picking.state != 'done':
                continue
            return_id = self.wiz_ret_obj.with_context({
                'active_id': picking.id,
                'active_ids': picking.ids,
                'active_model': 'stock.picking'}).create({})
            return_id.product_return_moves.write({'quantity': 5.0})
            nw_pick = return_id.create_returns()
            picking_id = safe_eval(nw_pick['domain'])[0][2][0]
            wiz = self.wiz_obj.with_context({
                'active_id': picking_id,
                'active_ids': [picking_id],
                'active_model': 'stock.picking'
            }).create({'picking_id': picking_id})
            wiz.item_ids.write({'quantity': 5.0})
            wiz.do_detailed_transfer()
            with self.assertRaisesRegexp(ValidationError, self.msg_error):
                sale.action_cancel_allow()
            return_id = self.wiz_ret_obj.with_context({
                'active_id': picking.id,
                'active_ids': picking.ids,
                'active_model': 'stock.picking'}).create({})
            return_id.product_return_moves.write({'quantity': 5.0})
            nw_pick = return_id.create_returns()
            picking_id = safe_eval(nw_pick['domain'])[0][2][0]
            wiz = self.wiz_obj.with_context({
                'active_id': picking_id,
                'active_ids': [picking_id],
                'active_model': 'stock.picking'
            }).create({'picking_id': picking_id})
            wiz.item_ids.write({'quantity': 5.0})
            wiz.do_detailed_transfer()
            break
        sale.action_cancel_allow()
        self.assertEquals(sale.state, 'cancel', 'Sale not cancelled')
