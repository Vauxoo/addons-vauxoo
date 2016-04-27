# coding: utf-8
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-Today OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

from openerp.osv import osv, fields


class SearchDuplicatedTask(osv.TransientModel):

    """  """

    def search_task_method(self, cr, uid, operator, name, list_ids,
                           context=None):
        if context is None:
            context = {}
        task_obj = self.pool.get('project.task')
        task_ids = task_obj.search(cr, uid,
                                   [(operator, 'ilike', name),
                                    ('id', 'not in', list(set(list_ids)))],
                                   context=context)

        return task_ids

    def get_match_task(self, cr, uid, full_name, context=None):
        """Search task that match with this full_name
        @param full_name: Name to search if match whit other task name or
        description
        """
        if context is None:
            context = {}
        lines = []
        long_name = ''
        count = 0
        list_task_ids = context.get('active_ids', [])
        for name in full_name.split(' '):
            if not count:
                long_name = '%' + name + '%'
                if len(long_name) > 5:
                    task_ids = self.search_task_method(cr, uid, 'name',
                                                       long_name,
                                                       list_task_ids,
                                                       context)
                    lines += [{
                        'parent': False, 'task_id': ids} for ids in task_ids]
                    list_task_ids += task_ids
                count += 1

            else:
                if len(name) > 3:
                    task_ids = self.search_task_method(cr, uid, 'description',
                                                       '%' + name + '%',
                                                       list_task_ids,
                                                       context)

                    lines += [{
                        'parent': False, 'task_id': ids} for ids in task_ids]
                    list_task_ids += task_ids
                    task_ids = self.search_task_method(cr, uid, 'name',
                                                       '%' + name + '%',
                                                       list_task_ids,
                                                       context)
                    list_task_ids += task_ids
                    lines += [{
                        'parent': False, 'task_id': ids} for ids in task_ids]
                long_name = '%' + long_name + '%' + name
                task_ids = self.search_task_method(cr, uid, 'description',
                                                   long_name,
                                                   list_task_ids,
                                                   context)
                list_task_ids += task_ids
                for ids in task_ids:
                    lines.insert(0, {'parent': False, 'task_id': ids})
                task_ids = self.search_task_method(cr, uid, 'name',
                                                   long_name,
                                                   list_task_ids,
                                                   context)
                list_task_ids += task_ids
                for ids in task_ids:
                    lines.insert(0, {'parent': False, 'task_id': ids})
        return lines

    def default_get(self, cr, uid, fields, context=None):
        """Overwrite default get method to search tasks  matching the task name
        with other tasks in system

        """
        if context is None:
            context = {}
        lines = False
        res = super(SearchDuplicatedTask, self).default_get(cr, uid, fields,
                                                            context=context)
        if context.get('task_name', False):
            lines = self.get_match_task(cr, uid, context.get('task_name'),
                                        context)
        res.update({'line_ids': lines})

        return res

    _name = 'search.duplicated.task'

    _columns = {
        'line_ids': fields.one2many('search.duplicated.task.line',
                                    'main_id',
                                    'Lines',
                                    help='Tasks which match with this '
                                    'description '),
        'task_name': fields.char('Task Name', 128, help='Task name for '
                                 'search other '
                                 'tasks that match '
                                 'with this name '),


    }

    def onchange_get_match_task(self, cr, uid, ids, name, context=None):
        if context is None:
            context = {}

        res = {'value': {}}
        if name:
            lines = self.get_match_task(cr, uid, name, context)
            res['value'].update({'line_ids': lines})

        return res

    def launch_task(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        task_id = []
        for wz in self.browse(cr, uid, ids, context=context):
            for line in wz.line_ids:
                if line.parent:
                    task_id = line.task_id and line.task_id.id
                    break

        obj_model = self.pool.get('ir.model.data')
        model_data_ids = obj_model.search(cr, uid,
                                          [('model', '=', 'ir.ui.view'),
                                           ('name', '=', 'view_task_form2')])
        resource_id = obj_model.read(cr, uid, model_data_ids,
                                     fields=['res_id'])[0]['res_id']
        res = {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'project.task',
            'views': [(resource_id, 'form')],
            'res_id': task_id,
            'type': 'ir.actions.act_window',
            'context': {},
        }

        return res

    def set_task(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        task_obj = self.pool.get('project.task')
        if context.get('active_ids', False):
            for wz in self.browse(cr, uid, ids, context=context):
                for line in wz.line_ids:
                    if line.parent:
                        task_obj.write(cr, uid, context.get('active_ids'),
                                       {'duplicated': True,
                                        'duplicated_task_id': line.task_id.id},
                                       context=context)

        return True


class SearchDuplicatedTaskLine(osv.TransientModel):

    """  """
    _name = 'search.duplicated.task.line'

    _columns = {
        'parent': fields.boolean('Parent',
                                 help='Main task of which this is '
                                 'duplicate'),
        'main_id': fields.many2one('search.duplicated.task',
                                   'Main'),
        'task_id': fields.many2one('project.task',
                                   'Tasks',
                                   help='Tasks that match with this name '),
    }
