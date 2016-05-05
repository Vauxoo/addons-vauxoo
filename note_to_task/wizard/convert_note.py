# coding: utf-8
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
################# Credits######################################################
#    Coded by: Luis Escobar <luis@vauxoo.com>
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

from openerp.osv import fields, osv


class ConvertNoteTask(osv.TransientModel):

    """Convert Note to Task Wizard"""

    _name = 'convert.note.task'

    _columns = {
        'estimated_time': fields.float('Estimated Time', help="""Estimated Time to Complete the
                Task""", required=True),
        'project_id': fields.many2one('project.project', 'Project', help='Project Linked', required=True),
        'date_deadline': fields.date('Deadline', help='Date to complete the Task', required=True),
    }

    def create_task(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        cvt_brw = self.browse(cr, uid, ids, context=context)
        task_obj = self.pool.get('project.task')
        note_obj = self.pool.get('note.note')
        note_brw = note_obj.browse(
            cr, uid, [context.get('active_id')], context=context)
        task_id = task_obj.create(cr, uid, {
            'name': note_brw[0].name,
            'description': note_brw[0].memo,
            'project_id': cvt_brw[0].project_id.id,
            'user_id': uid,
            'date_deadline': cvt_brw[0].date_deadline,
        }, context=context)
        note_obj.write(cr, uid, [context.get('active_id')], {
            'open': False,
        })
        obj_model = self.pool.get('ir.model.data')
        model_data_ids = obj_model.search(
            cr, uid, [('model', '=', 'ir.ui.view'),
                      ('name', '=', 'view_task_form2')])
        resource_id = obj_model.read(cr, uid, model_data_ids,
                                     fields=['res_id'])[0]['res_id']
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'project.task',
            'views': [(resource_id, 'form')],
            'res_id': task_id,
            'type': 'ir.actions.act_window',
            'context': {},
        }
