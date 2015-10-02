# coding: utf-8
#
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
#
#    Coded by: Juan Carlos Funes(juan@vauxoo.com)
#
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

from openerp.osv import fields, osv


class EmployeeUserWizard(osv.TransientModel):
    _name = 'employee.user.wizard'

    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}

        res = super(EmployeeUserWizard, self).default_get(
            cr, uid, fields, context=context)
        user_ids = context.get('active_ids', False)
        if user_ids:
            all_ids = self.get_unconfigured_cmp(cr, uid, context)
            user_ids = [i for i in user_ids if i in all_ids]
            res.update({'user_ids': user_ids})

        return res

    _columns = {
        'user_ids': fields.many2many('res.users', 'res_users_wizard_rel', 'user_wizard_id', 'user_id', 'Users'),
    }

    _defaults = {
        #'user_ids': _default_users
    }

    def get_unconfigured_cmp(self, cr, uid, context=None):
        """ get the list of users that have not been configured yet """
        if context is None:
            context = {}
        user_ids = self.pool.get('res.users').search(
            cr, uid, [], context=context)
        cr.execute("""SELECT users.id FROM res_users as users
                                        JOIN resource_resource as resource
                                        ON resource.user_id = users.id  GROUP BY users.id""")
        configured_cmp = [r[0] for r in cr.fetchall()]
        return list(set(user_ids) - set(configured_cmp))

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        if context is None:
            context = {}
        res = super(EmployeeUserWizard, self).fields_view_get(
            cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=False)
        cmp_select = []
        # display in the widget selection only the users that haven't been
        # configured yet
        unconfigured_cmp = self.get_unconfigured_cmp(cr, uid, context=context)
        for field in res['fields']:
            if field == 'user_ids':
                res['fields'][field]['domain'] = [
                    ('id', 'in', unconfigured_cmp)]
                res['fields'][field]['selection'] = [('', '')]
                if unconfigured_cmp:
                    cmp_select = [(line.id, line.name)
                                  for line in self.pool.get('res.users').browse(cr, uid, unconfigured_cmp)]
                    res['fields'][field]['selection'] = cmp_select
        return res

    def create_employee(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        employee_list = []
        ids = isinstance(ids, (int, long)) and [ids] or ids
        employee_obj = self.pool.get('hr.employee')
        resource_obj = self.pool.get('resource.resource')
        users_obj = self.pool.get('res.users')
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        form = self.read(cr, uid, ids, context=context)
        users_ids = form[0]['user_ids'] or self.get_unconfigured_cmp(
            cr, uid, context=context)
        for user in users_obj.browse(cr, uid, users_ids, context):
            vals_resource = {'name': user.name or False,
                             'user_id': user.id or False}
            resource_id = resource_obj.create(
                cr, uid, vals_resource, context=context)
            vals_employee = {'name_related': user.name or False,
                             'resource_id': resource_id or False,
                             'image': user.image or False,
                             'company_id': user.company_id.id or False,
                             'work_email': user.email or False}
            employee_id = employee_obj.create(
                cr, uid, vals_employee, context=context)
            employee_id = int(employee_id)
            employee_list.append(employee_id)
        if employee_list:
            result = mod_obj.get_object_reference(
                cr, uid, 'hr', 'open_view_employee_list_my')
            id = result and result[1] or False
            result = act_obj.read(cr, uid, [id], context=context)[0]
            # choose the view_mode accordingly
            result[
                'domain'] = "[('id','in',[" + ','.join(map(str, employee_list)) + "])]"
            result['res_id'] = employee_list and employee_list[0] or False
            # choose the order
            result['views'] = [
                (False, u'tree'), (False, u'kanban'), (False, u'form')]
            return result
        return True
