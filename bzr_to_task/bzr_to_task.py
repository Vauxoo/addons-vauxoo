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
        'url_branch': fields.char('Url Branch', 264, help="Here you must place"
             " the bazar url without 's' in the protocol ie."
             " http://bazaar.launchpad.net/~vauxoo/addons-vauxoo/7.0"),
        'merge_proposal': fields.char('Merge Proposal', 264),
        'blueprint': fields.char('Blueprint', 264),
        'res_id': fields.char('Revno', 64),
        'from_revno': fields.integer('From Revno')
    }
    _defaults = {
        'res_id': 0,
    }

    def get_works(self, cr, uid, ids, context=None):
        user_obj = self.pool.get('res.users')
        task_obj = self.pool.get('project.task')
        obj_this = self.browse(cr, uid, ids)[0]
        url = obj_this.url_branch
        res_id = obj_this.res_id
        inferior = obj_this.from_revno
        if url and res_id and inferior and int(res_id) > inferior:
            project_branch = branch.Branch.open(url)
            b_revno = project_branch.revno()
            if res_id:
                repo = project_branch.repository
                revision_map = project_branch.get_revision_id_to_revno_map()
                if revision_map:
                    for revision_id in revision_map.keys():
                        task_data = {}
                        revision = repo.get_revision(revision_id)
                        date = datetime.datetime.fromtimestamp(int(
                            revision.timestamp)).strftime('%Y-%m-%d %H:%M:%S')
                        splitted_revision_id = revision_id.split('-')
                        email = revision_id[0]
                        user_ids = user_obj.search(
                            cr, uid, [('email', '=', email)])
                        task_data = {
                            'name': revision.message,
                            'date_deadline': date,
                            'revno': revision_map[revision_id][0],
                        }
                        if user_ids:
                            task_data['user_id'] = user_ids[0]
                        task_ids = task_obj.search(cr, uid, [('project_id', '=', ids[
                                                   0]), ('revno', '=', task_data['revno'])])
                        if not task_ids:
                            if inferior and inferior <= task_data['revno'] and int(res_id) >= task_data['revno']:
                                self.write(cr, uid, ids, {
                                           'tasks': [(0, 0, task_data)]})
        else:
            raise osv.except_osv(('Error'), ('Fields: URL Branch, From Revno and Revno are required to execute this operation, \
                also From Revno must be minor than Revno'))
        return True


class sprint_kanban_tasks(osv.Model):
    _inherit = 'project.task'
    _columns = {
        'revno': fields.integer('Revno'),
        'from_revno': fields.integer('From Revno'),
        'url_branch': fields.char('Url Branch', 264, help="Here you must place"
             " the bazar url without 's' in the protocol ie."
             " http://bazaar.launchpad.net/~vauxoo/addons-vauxoo/7.0"),
    }
    _defaults = {
        'res_id': 0,
    }

    def set_work_time(self, cr, uid, ids, context=None):
        rev_date = {}
        task_work_obj = self.pool.get('project.task.work')
        for task in self.browse(cr, uid, ids):
            for tw in task.work_ids:
                rev_date[tw.revno] = tw.date,
            for tw in task.work_ids:
                previous = tw.revno - 1
                if rev_date.get(previous, False):
                    p_date = datetime.datetime.strptime(
                        rev_date[previous][0], '%Y-%m-%d %H:%M:%S')
                    actual = datetime.datetime.strptime(
                        tw.date, '%Y-%m-%d %H:%M:%S')
                    result = actual - p_date
                    if float(result.seconds) / 60 / 60 > 0.16:
                        hours = float(result.seconds) / 60 / 60
                    else:
                        hours = 0.16
                    max_date = max(rev_date.itervalues())[0]
                    deadline = datetime.datetime.strptime(
                        max_date, '%Y-%m-%d %H:%M:%S')
                    deadline = deadline + datetime.timedelta(days=1)
                    task_work_obj.write(cr, uid, [tw.id], {'hours': hours})

        return deadline

    def get_works(self, cr, uid, ids, context=None):
        tw_obj = self.pool.get('project.task.work')
        user_obj = self.pool.get('res.users')
        obj_this = self.browse(cr, uid, ids)[0]
        url = obj_this.url_branch
        res_id = obj_this.res_id
        inferior = obj_this.from_revno
        if url and res_id and inferior and int(res_id) > inferior:
            task_branch = branch.Branch.open(url)
            b_revno = task_branch.revno()
            if res_id:
                repo = task_branch.repository
                revision_map = task_branch.get_revision_id_to_revno_map()
                if revision_map:
                    for k in revision_map.keys():
                        tw_data = {}
                        revision = repo.get_revision(k)
                        date = datetime.datetime.fromtimestamp(int(
                            revision.timestamp)).strftime('%Y-%m-%d %H:%M:%S')
                        revision_id = k.split('-')
                        email = revision_id[0]
                        user_ids = user_obj.search(
                            cr, uid, [('email', '=', email)])
                        tw_data = {
                            'name': revision.message,
                            'date': date,
                            'revno': revision_map[k][0],
                            'hours': 0,
                        }
                        if user_ids:
                            tw_data['user_id'] = user_ids[0]
                        else:
                            tw_data['user_id'] = uid
                        tw_ids = tw_obj.search(cr, uid, [('task_id', '=', ids[
                                               0]), ('revno', '=', tw_data['revno'])])
                        if not tw_ids:
                            if inferior and inferior <= tw_data['revno'] and int(res_id) >= tw_data['revno']:
                                self.write(cr, uid, ids, {
                                           'work_ids': [(0, 0, tw_data), ], })
                    deadline = self.set_work_time(cr, uid, ids, context)
                    self.write(cr, uid, ids, {'date_deadline': deadline})
        else:
            raise osv.except_osv(('Error'), ('Fields: URL Branch, From Revno and Revno are required to execute this operation, \
                also From Revno must be minor than Revno'))
        return True


class project_task_work(osv.Model):
    _inherit = 'project.task.work'
    _columns = {
        'revno': fields.integer('Revno'),
    }
