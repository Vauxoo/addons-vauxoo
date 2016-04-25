# coding: utf-8
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
# Credits #####################################################################
#    Coded by: Katherine Zaoral <kathy@vauxoo.com>
#    Planified by: Humberto Arocha <hbto@vauxoo.com>,
#                  Katherine Zaoral <kathy@vauxoo.com>
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

from openerp.osv import osv, fields


class PurchaseRequisition(osv.Model):

    """This is an extension of the purchase requisition model to add the
    functionality to manage a suggested list of partners.
    """

    _inherit = 'purchase.requisition'
    _columns = {
        'suggested_supplier':
            fields.text('Suggested Suppliers'),
        'suggested_supplier_ids': fields.many2many(
            'res.partner',
            'purchase_requisition_suggested_suppliers_rel',
            'purchase_requisition_id', 'partner_id',
            'Suggested Suppliers',
            help=('The suppliers suggested to compete for the current'
                  ' purchase requisition.')),
        'supplier_ids': fields.many2many(
            'res.partner',
            'purchase_requisition_suppliers',
            'purchase_requisition_id', 'partner_id',
            'Suppliers',
            help=('The Suppliers that will participate in the tender. This'
                  ' suppliers can only be defined by the purchase analyst in'
                  ' the phase of Prepare Tenderplan.')),
        'single_source_justification':
            fields.text('Single Source Justification'),
    }

    def create_orders(self, cr, uid, ids, context=None):
        """This method create the quotations of the purchase requisition for all
        the partners given in the purchase requisition suggested partner.
        @return True
        """
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        func = self.make_purchase_order
        for req_brw in self.browse(cr, uid, ids, context=context):
            partner_ids = [po_brw.partner_id.id for po_brw in
                           req_brw.purchase_ids]
            for partner_brw in req_brw.supplier_ids:
                if partner_brw.id in partner_ids:
                    continue
                func(cr, uid, [req_brw.id], partner_brw.id, context=context)
        return True
