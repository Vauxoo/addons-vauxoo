#!/usr/bin/python
# -*- encoding: utf-8 -*-
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

class purchase_requisition(osv.Model):

    _inherit = 'purchase.requisition'
    _columns = {
        'department_id': fields.many2one(
            'hr.department',
            string='Department',
            help='The department where this purchase requisition belongs'),
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

    #def fields_view_get(self, cr, uid, view_id=None, view_type='form',
    #                    context=None, toolbar=False, submenu=False):
    #    """ 
    #    Filter the department by the ones the current user belongs.
    #    """
    #    context = context or {}
    #    res = super(purchase_requisition,self).fields_view_get(
    #        cr, uid, view_id=view_id, view_type=view_type, context=context,
    #        toolbar=toolbar, submenu=submenu)

    #    user_obj = self.pool.get('res.users')
    #    user_brw = user_obj.browse(cr, uid, uid, context=context)
    #    if 'department_id' in res['fields'].keys():
    #        dep_ids = [emp_brw.department_id.id for emp_brw in user_brw.employee_ids]
    #        res['fields']['department_id']['domain'] = [('id', 'in', dep_ids)]
    #    return res

    # TODO: This filter method is not working.
    #def fields_view_get(self, cr, uid, view_id=None, view_type='form',
    #                    context=None, toolbar=False, submenu=False):
    #    """ 
    #    Filter the department by the ones the user_id.employee_ids belongs.
    #    """
    #    context = context or {}
    #    res = super(purchase_requisition,self).fields_view_get(
    #        cr, uid, view_id=view_id, view_type=view_type, context=context,
    #        toolbar=toolbar, submenu=submenu)

    #    user_id = res['fields']['user_id'].get('selection', False) or uid
    #    user_obj = self.pool.get('res.users')
    #    emp_obj = self.pool.get('hr.employee')
    #    dep_obj = self.pool.get('hr.department')
    #    user_brw = user_obj.browse(cr, uid, user_id, context=context)
    #    if 'department_id' in res['fields'].keys():
    #        emp_ids = [emp_brw.id for emp_brw  in user_brw.employee_ids]
    #        dep_ids = [emp_brw.department_id.id for emp_brw in user_brw.employee_ids]
    #        dep_selected = dep_obj._name_search(cr, uid, '', [('member_ids', 'in',
    #            emp_ids)], context=context, limit=None, name_get_uid=1)
    #        res['fields']['department_id']['selection'] = dep_selected
    #        res['fields']['department_id']['domain'] = [('id', 'in', dep_ids)]

    #    return res

