# -*- encoding: utf-8 -*-
########################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
########################################################################
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
from openerp import netsvc

from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp


class purchase_requisition_line(osv.Model):
    _inherit = "purchase.requisition.line"

    _columns = {
        'name': fields.text('Description', required=True),
        'account_analytic_id': fields.many2one(
            'account.analytic.account', 'Analytic Account',
                help='This field is used to assign the selected'\
                ' analytic account to the line of the purchase order'),
    }

    def onchange_product_id(self, cr, uid, ids, product_id,
                            product_uom_id, context=None):
        product_obj = self.pool.get('product.product')
        res = {'value': {'name': ''}}
        if product_id:
            product_name = product_obj.name_get(
                cr, uid, product_id, context=context)
            dummy, name = product_name and product_name[0] or (False,
                                                                False)

            product = product_obj.browse(cr, uid, product_id,
                                                    context=context)
            if product.description_purchase:
                name += '\n' + product.description_purchase
            res['value'].update({'name': name})
        return res

purchase_requisition_line()


class purchase_requisition(osv.Model):
    _inherit = "purchase.requisition"

    def make_purchase_order(self, cr, uid, ids, partner_id,
                                    context=None):  # method override
        """
        Create New RFQ for Supplier
        """
        if context is None:
            context = {}
        assert partner_id, 'Supplier should be specified'
        purchase_order = self.pool.get('purchase.order')
        purchase_order_line = self.pool.get('purchase.order.line')
        res_partner = self.pool.get('res.partner')
        fiscal_position = self.pool.get('account.fiscal.position')
        supplier = res_partner.browse(cr, uid, partner_id,
                                                        context=context)
        supplier_pricelist =\
                supplier.property_product_pricelist_purchase or False
        res = {}
        for requisition in self.browse(cr, uid, ids, context=context):
            if supplier.id in filter(lambda x: x,
                [rfq.state <> 'cancel' and rfq.partner_id.id or None\
                    for rfq in requisition.purchase_ids]):
                raise osv.except_osv(
                    _('Warning!'), _('You have already one %s purchase'\
                    ' order for this partner, you must cancel this'\
                    ' purchase order to create a new quotation.') %\
                                                              rfq.state)
            location_id = requisition.warehouse_id.lot_input_id.id
            purchase_id = purchase_order.create(cr, uid, {
                'origin': requisition.name,
                'partner_id': supplier.id,
                'pricelist_id': supplier_pricelist.id,
                'location_id': location_id,
                'company_id': requisition.company_id.id,
                'fiscal_position': supplier.property_account_position\
                    and supplier.property_account_position.id or False,
                'requisition_id': requisition.id,
                'notes': requisition.description,
                'warehouse_id': requisition.warehouse_id.id,
            })
            res[requisition.id] = purchase_id
            for line in requisition.line_ids:
                product = line.product_id
                seller_price, qty, default_uom_po_id, date_planned =\
                    self._seller_details(cr, uid, line, supplier,
                                                        context=context)
                taxes_ids = product.supplier_taxes_id
                taxes = fiscal_position.map_tax(
                    cr, uid, supplier.property_account_position,
                                                            taxes_ids)
                purchase_order_line.create(cr, uid, {
                    'order_id': purchase_id,
                    # start custom change
                    #'name': product.partner_ref,
                    'name': line.name,
                    # end custom change
                    'product_qty': qty,
                    'product_id': product.id,
                    'product_uom': default_uom_po_id,
                    'price_unit': seller_price,
                    'date_planned': date_planned,
                    'taxes_id': [(6, 0, taxes)],
                    'account_analytic_id': line.account_analytic_id\
                            and line.account_analytic_id.id or False,
                }, context=context)
        if res:
            requisition_user = self.browse(
                cr, uid, res.keys()[0], context=context).user_id
            purchase_order_obj = self.pool.get('purchase.order')
            purchase_order_obj.write(
                            cr, uid, res[res.keys()[0]],
                            {'rfq_user_id': requisition_user.id})
        return res


class purchase_order(osv.Model):
    _inherit = "purchase.order"

    _columns = {
        'rfq_user_id': fields.many2one('res.users', 'Requisitor'),
    }
