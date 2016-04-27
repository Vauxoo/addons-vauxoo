# coding: utf-8
############################################################################
#    Module Writen to OpenERP, Open Source Management Solution             #
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).            #
#    All Rights Reserved                                                   #
# Credits######################################################
#    Coded by: Maria Gabriela Quilarque  <gabrielaquilarque97@gmail.com>   #
#    Planified by: Nhomar Hernandez                                        #
#    Finance by: Helados Gilda, C.A. http://heladosgilda.com.ve            #
#    Audited by: Humberto Arocha humberto@openerp.com.ve                   #
############################################################################
#    This program is free software: you can redistribute it and/or modify  #
#    it under the terms of the GNU General Public License as published by  #
#    the Free Software Foundation, either version 3 of the License, or     #
#    (at your option) any later version.                                   #
#                                                                          #
#    This program is distributed in the hope that it will be useful,       #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of        #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
#    GNU General Public License for more details.                          #
#                                                                          #
#    You should have received a copy of the GNU General Public License     #
#    along with this program.  If not, see <http://www.gnu.org/licenses/>. #
############################################################################
import time
from openerp.report import report_sxw


class ProjectIssue(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context=None):
        """Initlize a report parser, add custome methods to localcontext
        @param cr: cursor to database
        @param user: id of current user
        @param name: name of the reports it self
        @param context: context arguments, like lang, time zone
        """
        super(ProjectIssue, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
                                 'time': time,
                                 'get_issue_by_project': self._get_issue_by_project,
                                 })

    def _get_issue_by_project(self, issues, form):
        pool = pooler.get_pool(self.cr.dbname)
        res = []
        proj_ids = []
        part_ids = []
        aux = []
        for issue in issues:
            aux.append(issue.id)
            if issue and issue.partner_id and issue.partner_id.id not in part_ids:
                part_ids.append(issue.partner_id.id)
            if issue and issue.project_id and issue.project_id.id not in proj_ids:
                proj_ids.append(issue.project_id.id)

        parts = pool.get('res.partner').name_get(self.cr, self.uid, part_ids)
        for part in parts:
            res.append({
                       'name': part[1],
                       'project': self._get_project(form, aux, proj_ids, part[0])})
        return res

    def _get_project(self, form, issues, proj_ids, partner):
        pool = pooler.get_pool(self.cr.dbname)
        res = []
        aux = []
        pi_ids = pool.get('project.issue').search(
            self.cr, self.uid, [('partner_id', '=', partner)])
        for issue in pool.get('project.issue').browse(self.cr, self.uid, pi_ids):
            issue and issue.project_id and aux.append(issue.project_id.id)

        for proy in pool.get('project.project').browse(self.cr, self.uid, list(set(aux))):

            if proy.id in proj_ids:
                val = {
                    'name': proy.name,
                    'issue': self._get_issue(form, issues, proy, partner)
                }

                res.append(val)
        return res

    def _get_issue(self, form, issues, project, partner):
        res = []
        state = ''
        priority = ''
        pool = pooler.get_pool(self.cr.dbname)
        pi_ids = pool.get('project.issue').search(self.cr, self.uid, [(
            'project_id', '=', project.id), ('partner_id', '=', partner)])
        hours = 0.0
        total_hours_es = 0.0
        for pro_isu in pool.get('project.issue').browse(self.cr, self.uid, pi_ids):
            if pro_isu.id in issues:
                x = pool.get('project.issue').fields_get(
                    self.cr, self.uid, ['state', 'priority'])
                for i in x.get('state', {}).get('selection', []):
                    if i[0] == pro_isu.state:
                        state = i[1]

                for i in x.get('priority', {}).get('selection', []):
                    if i[0] == pro_isu.priority:
                        priority = i[1]

                hours1 = pro_isu.task_id.total_hours or 0
                hours = hours + hours1

                hours2 = pro_isu.task_id.planned_hours or 0
                total_hours_es = total_hours_es + hours2

                if not form.get('task'):
                    res.append({
                        'id': pro_isu.id,
                        'date': pro_isu.create_date,
                        'name': pro_isu.name,
                        'priority': priority,
                        'responsable': pro_isu.partner_address_id.name,
                        'progress': pro_isu.progress,
                        'state': state,
                        'category': pro_isu.categ_id.name,
                        'hours': pro_isu.task_id and pro_isu.task_id.total_hours or 0.0,
                        'hours_es': pro_isu.task_id and pro_isu.task_id.planned_hours or 0.0,
                        'total_hours': hours,
                        'total_hours_es': total_hours_es,
                        'task': False
                    })
                else:
                    res.append({
                        'id': pro_isu.id,
                        'date': pro_isu.create_date,
                        'name': pro_isu.name,
                        'priority': priority,
                        'responsable': pro_isu.partner_address_id.name,
                        'progress': pro_isu.progress,
                        'state': state,
                        'category': pro_isu.categ_id.name,
                        'hours': pro_isu.task_id and pro_isu.task_id.total_hours or 0.0,
                        'hours_es': pro_isu.task_id and pro_isu.task_id.planned_hours or 0.0,
                        'total_hours_es': total_hours_es,
                        'task': pro_isu.task_id and self._get_task(pro_isu.task_id) or []
                    })
        return res

    def _get_task(self, task_id):
        pool = pooler.get_pool(self.cr.dbname)
        res = []
        task = pool.get('project.task').browse(self.cr, self.uid, task_id.id)
        x = pool.get('project.task').fields_get(self.cr, self.uid, ['state'])
        for i in x.get('state', {}).get('selection', []):
            if i[0] == task.state:
                state = i[1]
        res.append({
                   'create_date': task.create_date,
                   'date_deadline': task.date_deadline,
                   'name': task.name,
                   'asigned_to': task.user_id.name,
                   'planned_hours': task.planned_hours and task.planned_hours or '0.0',
                   'remaining_hours': task.remaining_hours and task.remaining_hours or '0.0',
                   'cost': '0',
                   'state': state,
                   })
        return res

report_sxw.report_sxw(
    'report.project.issuereport',
    'project.issue',
    'addons/project_issue_report2/report/project_issue.rml',
    parser=ProjectIssue
)
