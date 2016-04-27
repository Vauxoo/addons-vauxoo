# -*- coding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
###############################################################################
#    Credits:
#    Coded by: Katherine Zaoral <kathy@vauxoo.com>
#    Planified by: Katherine Zaoral <kathy@vauxoo.com>
#    Audited by: Katherine Zaoral <kathy@vauxoo.com>
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

from openerp.tests import common
import time


class TestStockCommon(common.TransactionCase):

    def setUp(self):
        super(TestStockCommon, self).setUp()
        self.product = self.ref('product.product_product_4')
        self.product2 = self.ref('product.product_product_35')
        self.product3 = self.ref('product.product_product_8')
        self.partner = self.ref('base.res_partner_1')
        self.location = self.ref('stock.stock_location_stock')
        self.supp_location = self.ref('stock.stock_location_suppliers')
        self.picking_type_in = self.ref('stock.picking_type_in')
        self.order_obj = self.env['purchase.order']
        self.product_obj = self.env['product.product']
        self.picking_obj = self.env['stock.picking']
        self.wiz_obj = self.env['stock.transfer_details']

    def create_pol(self, order, product=False):
        """Create a new purchase order line for the given purchase order taking
        as input only the product
        """
        product = self.product_obj.browse(product or self.product)
        order.write({
            'order_line': [(0, 0, {
                'product_id': product.id,
                'product_qty': 10.0,
                'product_uom': product.uom_id.id,
                'price_unit': product.price,
                'name': product.name_template,
                'date_planned': time.strftime('%Y-%m-%d'),
            })]})

    def create_po(self, invoice_method='picking'):
        """ Create a purchase order """
        order = self.order_obj.create({
            'partner_id': self.partner,
            'location_id': self.location,
            'pricelist_id': 1,
            'invoice_method': invoice_method,
        })
        return order

    def create_and_validate_po(self):
        """ Create and Validate purchase order """
        order = self.create_po()
        self.create_pol(order)
        self.create_pol(order, self.product2)
        order.signal_workflow('purchase_confirm')
        return order

    def add_move(self, picking):
        """ add new line to the picking """
        product = self.product_obj.browse(self.product3)
        picking.write({'move_lines': [(0, 0, {
            'name': product.name,
            'product_id': product.id,
            'product_uom': product.uom_id.id,
            'product_uom_qty': 3,
            'location_id': self.supp_location,
            'location_dest_id': self.location,
        })]})

    def remove_move(self, picking):
        """remove move line from stock picking
        """
        move2 = picking.move_lines.filtered(
            lambda line: line.product_id.id == self.product2)
        picking.write({'move_lines': [(3, move2.id)]})
        return True
