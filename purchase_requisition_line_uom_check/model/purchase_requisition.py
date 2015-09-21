# coding: utf-8
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

from openerp.osv import osv


class PurchaseRequisitionLine(osv.Model):
    _inherit = "purchase.requisition.line"

    def _check_same_uom_category(self, cr, uid, ids, context=None):
        for line_brw in self.browse(cr, uid, ids, context=context):
            if not line_brw.product_uom_id:
                return False
            if line_brw.product_id.uom_id.category_id.id != \
                    line_brw.product_uom_id.category_id.id:
                return False
        return True

    _constraints = [
        (_check_same_uom_category,
         ('Selected Unit of Measure does not belong to the same category as '
          'the product Unit of Measure.'), ['product_uom_id']),
    ]
