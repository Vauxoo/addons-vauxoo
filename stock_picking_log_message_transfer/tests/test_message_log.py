# coding: utf-8
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
###############################################################################
#    Credits:
#    Coded by: Yanina Aular <yani@vauxoo.com>
#    Planified by: Gabriela Quilarque <gabriela@vauxoo.com>
#    Audited by: Nhomar Hernandez <nhomar@vauxoo.com>
###############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################

from datetime import datetime
from openerp.tests.common import TransactionCase


class TestMessageLog(TransactionCase):
    """Search last message and check that must be about Transfer
    """

    def test_01(self):
        self.company = self.env.user.company_id
        partner = self.env.ref('base.res_partner_12')
        imac = self.env.ref('product.product_product_8')

        warehouse = self.env.ref('stock.warehouse0')
        warehouse.write({"reception_steps": "one_step"})
        currency = self.env.ref('base.EUR')
        purchase_obj = self.env['purchase.order']
        purchase = purchase_obj.create({
            'name': 'Order Tests to RMA',
            'company_id': self.company.id,
            'partner_id': partner.id,
            'currency_id': currency.id,
            'date_order': '2015-05-08 18:17:05',
            'picking_type_id': warehouse.in_type_id.id,
        })

        purchase_line_obj = self.env['purchase.order.line']
        purchase_line_obj.create({
            'name': imac.name,
            'product_id': imac.id,
            'price_unit': imac.standard_price,
            'order_id': purchase.id,
            'product_qty': 1.0,
            'company_id': self.company.id,
            'product_uom': self.env.ref('product.product_uom_unit').id,
            'date_planned': datetime.now().strftime('%Y-%m-%d'),
        })

        purchase.button_confirm()
        purchase.button_approve()
        picking = purchase.picking_ids[0]

        move = picking.move_lines[0]
        stock_pack_obj = self.env['stock.pack.operation']
        picking = move.picking_id
        wizard_id = stock_pack_obj.create({
            'picking_id': picking.id,
            'product_qty': move.product_uom_qty,
            'product_uom_id': self.env.ref('product.product_uom_unit').id,
            'location_id': picking.location_id.id,
            'location_dest_id': picking.location_dest_id.id,
            'product_id': move.product_id.id,
            'qty_done': move.product_uom_qty,
        })

        mac_1 = self.env['stock.production.lot'].create({
            'product_id': imac.id,
            'name': 'Test Lot 16567 %s' % picking.move_lines[0].id,
        })

        stock_pack_lot = self.env['stock.pack.operation.lot']
        stock_pack_lot.create({
            'operation_id': wizard_id.id,
            'lot_id': mac_1.id,
        })

        stock_backorder_confirmation = \
            self.env["stock.backorder.confirmation"]
        backorder = stock_backorder_confirmation.create({
            "pick_id": picking.id,
        })
        backorder.process()

        picking_msg = picking.message_ids.search([
            ('body', 'ilike', '%Picking transfered%')])
        self.assertTrue(picking_msg, "The message in log is not correct")
