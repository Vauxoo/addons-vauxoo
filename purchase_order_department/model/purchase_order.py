# coding: utf-8
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
############# Credits #########################################################
#    Coded by: Katherine Zaoral <kathy@vauxoo.com>
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

from openerp.osv import osv, fields


class PurchaseOrder(osv.Model):

    _inherit = 'purchase.order'
    _columns = {
        'department_id': fields.many2one(
            'hr.department',
            string='Department',
            help='The department where this purchase order belongs'),
    }

    def onchange_user_id(self, cr, uid, ids, user_id, context=None):
        """ Return the department depending of the user.
        @param user_id: user id
        """
        context = context or {}
        res = {}
        ru_obj = self.pool.get('res.users')
        if user_id:
            ru_brw = ru_obj.browse(cr, uid, user_id, context=context)
            department_id = (ru_brw.employee_ids
                             and ru_brw.employee_ids[0].department_id
                             and ru_brw.employee_ids[0].department_id.id or False)
            res.update({'value': {'department_id': department_id}})
        return res


class PurchaseRequisition(osv.Model):

    _inherit = "purchase.requisition"

    def make_purchase_order(self, cur, uid, ids, partner_id, context=None):
        """Over write the method to also extract the department_id from the
        purchase requisition.
        """
        context = context or {}
        res = super(PurchaseRequisition, self).make_purchase_order(
            cur, uid, ids, partner_id, context=context)
        if res:
            req_id = res.keys()[0]
            req_brw = self.browse(cur, uid, req_id, context=context)
            po_obj = self.pool.get('purchase.order')
            po_obj.write(cur, uid, res[req_id], {'department_id':
                                                 req_brw.department_id.id}, context=context)
        return res
