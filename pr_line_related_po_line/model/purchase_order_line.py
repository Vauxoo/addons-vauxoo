# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
############# Credits #########################################################
#    Coded by: Yanina Aular <yani@vauxoo.com>
#    Planified by: Humberto Arocha <hbto@vauxoo.com>
#    Audited by: Humberto Arocha <hbto@vauxoo.com>
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

from openerp.osv import fields, osv
from openerp.tools.translate import _


class purchase_order_line(osv.Model):

    _inherit = 'purchase.order.line'

    _columns = {
        'purchase_requisition_line_id': fields.many2one('purchase.requisition.line', "Purchase \
                Requisition Line"),
    }


class purchase_requisition(osv.Model):

    _inherit = 'purchase.requisition'

    def make_purchase_order(self, cr, uid, ids, partner_id, context=None):
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
        supplier = res_partner.browse(cr, uid, partner_id, context=context)
        supplier_pricelist = supplier.property_product_pricelist_purchase or False
        res = {}
        for requisition in self.browse(cr, uid, ids, context=context):
            if supplier.id in filter(lambda x: x, [rfq.state <> 'cancel' and rfq.partner_id.id or None for rfq in requisition.purchase_ids]):
                raise osv.except_osv(_('Warning!'), _('You have already one %s purchase order for this partner, you must cancel this purchase order to create a new quotation.') % rfq.state)
            location_id = requisition.warehouse_id.lot_input_id.id
            purchase_id = purchase_order.create(cr, uid, {
                'origin': requisition.name,
                'partner_id': supplier.id,
                'pricelist_id': supplier_pricelist.id,
                'location_id': location_id,
                'company_id': requisition.company_id.id,
                'fiscal_position': supplier.property_account_position and supplier.property_account_position.id or False,
                'requisition_id': requisition.id,
                'notes': requisition.description,
                'warehouse_id': requisition.warehouse_id.id,
            })
            res[requisition.id] = purchase_id
            for line in requisition.line_ids:
                product = line.product_id
                if product:
                    seller_price, qty, default_uom_po_id, date_planned = self._seller_details(cr, uid, line, supplier, context=context)
                else:
                    seller_price, qty, default_uom_po_id, date_planned = self._seller_details_without_product(cr, uid, line, supplier, context=context)
                taxes_ids = product.supplier_taxes_id
                taxes = fiscal_position.map_tax(cr, uid, supplier.property_account_position, taxes_ids)
                purchase_order_line.create(cr, uid, {
                    'order_id': purchase_id,
                    # change
                    'purchase_requisition_line_id': line.id,
                    # end change
                    'name': product and product.partner_ref or '',
                    'product_qty': line.product_qty or qty,
                    'product_id': product and product.id or False,
                    'product_uom': line.product_uom_id.id or default_uom_po_id,
                    'price_unit': seller_price,
                    'date_planned': date_planned,
                    'taxes_id': [(6, 0, taxes)],
                }, context=context)

        return res

    def _seller_details_without_product(self, cr, uid, requisition_line, supplier, context=None):
        default_uom_pol_id = self.pool.get('purchase.order.line')._get_uom_id(cr, uid, context=context)
        default_uom_po_id = requisition_line.product_uom_id and requisition_line.product_uom_id.id or default_uom_pol_id
        qty = requisition_line.product_qty
        seller_delay = 0.0
        seller_price = False
        date_planned = self._planned_date(requisition_line.requisition_id, seller_delay)
        return seller_price, qty, default_uom_po_id, date_planned
