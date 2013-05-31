#-*- coding:utf-8 -*-
#
#
#    OpenERP, Open Source Management Solution
#    Copyright (C)2010-  OpenERP SA (<http://openerp.com>). All Rights Reserved
#    oszckar@gmail.com
#
#    Developed by Oscar Alcala <oszckar@gmail.com>
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
from openerp import pooler, tools
from openerp.osv import fields, osv
from openerp.tools.translate import _
from bzrlib import branch
import datetime

class project_project(osv.Model):
    _inherit = 'project.project'
    _columns = {
        'sprint_id': fields.many2one('sprint.kanban', 'Sprint',
                                     ondelete="cascade"),
        'url_branch': fields.char('Url Branch', 264),
        'merge_proposal': fields.char('Merge Proposal', 264),
        'blueprint': fields.char('Blueprint', 264),
        'res_id': fields.char('Revno', 64),
            }

class sprint_kanban_tasks(osv.Model):
    _inherit = 'project.task'
    _defaults = {
        'res_id': 0,
            }
    def get_works(self, cr, uid, ids, context=None):
        tw_obj = self.pool.get('project.task.work')
        user_obj = self.pool.get('res.users')
        url = self.browse(cr, uid, ids)[0].url_branch
        res_id = self.browse(cr, uid, ids)[0].res_id
        if url:
            task_branch = branch.Branch.open(url)
            b_revno = task_branch.revno()
            if res_id:
                if res_id > b_revno:
                    repo = task_branch.repository
                    revision_map = task_branch.get_revision_id_to_revno_map()
                    if revision_map:
                        for k in revision_map.keys():
                            tw_data = {}
                            revision = repo.get_revision(k)
                            date = datetime.datetime.fromtimestamp(int(revision.timestamp)).strftime('%Y-%m-%d %H:%M:%S')
                            revision_id = k.split('-')
                            email = revision_id[0]
                            user_ids = user_obj.search(cr, uid, [('email','=',email)])
                            tw_data = {
                                'name': revision.message,
                                'date': date,
                                'revno': revision_map[k][0],
                                }
                            if user_ids:
                                tw_data['user_id'] = user_ids[0]
                            tw_ids = tw_obj.search(cr, uid, [('task_id','=',ids[0]),('revno','=',tw_data['revno'])])
                            if not tw_ids:
                                self.write(cr, uid, ids, {'res_id': b_revno, 'work_ids': [(0, 0, tw_data),],})
        return True

class project_task_work(osv.Model):
    _inherit = 'project.task.work'
    _columns = {
            'revno':fields.integer('Revno'),
            }
