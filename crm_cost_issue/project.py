#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: Luis Escobar                <luis@vauxoo.com>
#              María Gabriela Quilarque    <gabriela@openerp.com.ve>
#    Planified by: Nhomar Hernandez        <nhomar@openerp.com.ve>
#    Finance by: Helados Gilda, C.A. http://heladosgilda.com.ve
#    Audited by: María Gabriela Quilarque  <gabriela@openerp.com.ve>
#############################################################################
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
##########################################################################


from openerp.osv import osv, fields


class project_task(osv.Model):
    _inherit = 'project.task'

    def _hours_get(self, cr, uid, ids, field_names, args, context=None):
        data = super(project_task, self)._hours_get(
            cr, uid, ids, field_names, args, context=context)
        empl_obj = self.pool.get('hr.employee')
        for l in self.browse(cr, uid, ids, context=context):
            try:
                empl_ids = empl_obj.search(cr, uid, [
                                           ('user_id', '=', l.user_id.id)])
                empl = empl_obj.browse(cr, uid, empl_ids)[0]
                cost = empl.product_id.list_price * data[l.id]['total_hours']

            except Exception, e:
                cost = 0.0

            self.write(cr, uid, l.id, {'cost_per_task': cost})

        return data

    def _get_task(self, cr, uid, ids, context=None):
        return super(project_task, self)._get_task(cr, uid, ids,
                                                   context=context)

    _columns = {
        'effective_hours': fields.function(_hours_get, method=True,
                string='Hours Spent', multi='hours',
                help="Computed using the sum of the task work done.",
                store={
                    'project.task': (lambda self, cr, uid, ids, c={}: ids,
                        ['work_ids', 'remaining_hours', 'planned_hours'], 10),
                    'project.task.work': (_get_task, ['hours'], 10),
                }),
        'total_hours': fields.function(_hours_get, method=True,
                string='Total Hours', multi='hours',
                help="Computed as: Time Spent + Remaining Time.",
                store={
                    'project.task': (lambda self, cr, uid, ids, c={}: ids,
                        ['work_ids', 'remaining_hours', 'planned_hours'], 10),
                    'project.task.work': (_get_task, ['hours'], 10),
                }),
        'progress': fields.function(_hours_get, method=True,
                string='Progress (%)',
                multi='hours',
                group_operator="avg",
                help="Computed as: Time Spent / Total Time.",
                store={
                    'project.task': (lambda self, cr, uid, ids, c={}: ids,
                        ['work_ids', 'remaining_hours', 'planned_hours',
                         'state'], 10),
                    'project.task.work': (_get_task, ['hours'], 10),
                }),
        'delay_hours': fields.function(_hours_get, method=True,
                string='Delay Hours', multi='hours',
                help="Computed as difference of the time estimated by the\
                        project manager and the real time to close the task.",
                store={
                    'project.task': (lambda self, cr, uid, ids, c={}: ids,
                        ['work_ids', 'remaining_hours', 'planned_hours'], 10),
                    'project.task.work': (_get_task, ['hours'], 10),
                }),
        'cost_per_task': fields.float('Cost', readonly=True,
                help="Computed as: Hour Cost multiplied by Job Hours"),

    }
