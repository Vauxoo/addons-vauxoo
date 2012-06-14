# -*- encoding: utf-8 -*-
############################################################################
#    Module Writen to OpenERP, Open Source Management Solution             #
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).            #
#    All Rights Reserved                                                   #
###############Credits######################################################
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
import pooler
from report import report_sxw
from tools.translate import _

class project_issue(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context=None):
        """
        Initlize a report parser, add custome methods to localcontext 
        @param cr: cursor to database
        @param user: id of current user
        @param name: name of the reports it self
        @param context: context arguments, like lang, time zone 
        """
        super(project_issue, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
          'time': time,
          'get_issue_by_project': self._get_issue_by_project,
        })
    
    def _get_issue_by_project(self,issues,form):
        pool = pooler.get_pool(self.cr.dbname)
        res=[]
        proj_ids=[]
        part_ids=[]
        for issue in issues:
            if issue and issue.partner_id and issue.partner_id.id not in part_ids:
                part_ids.append(issue.partner_id.id)
            if issue and issue.project_id and issue.project_id.id not in proj_ids:
                proj_ids.append(issue.project_id.id)
        
        parts = pool.get('res.partner').name_get(self.cr, self.uid, part_ids)
        proys= pool.get('project.project').browse(self.cr, self.uid, proj_ids)
        for part in parts:
            for proy in proys:
                project = []
                pi= pool.get('project.issue').search(self.cr, self.uid, [('project_id', '=', proy.id)])
                for pro_isu in pool.get('project.issue').browse(self.cr, self.uid, pi):
                    if pro_isu in issues:
                        project.append({
                        'name':proy.name,
                        'issue':self._get_issue(form,pro_isu)
                        })
                res.append({'name':part[1],'project':project})
        
        return res
    
    def _get_issue(self,form,issue):
        res=[]
        if not form.get('task'):
            res.append({
                'id':issue.id,
                'date':issue.create_date,
                'name':issue.name,
                'priority':issue.priority,
                'responsable':issue.partner_address_id.name,
                'progress':issue.progress,
                'state':issue.state,
                'category':issue.categ_id.name,
            })
        else:
            res.append({
                'id':issue.id,
                'date':issue.create_date,
                'name':issue.name,
                'priority':issue.priority,
                'responsable':issue.partner_address_id.name,
                'progress':issue.progress,
                'state':issue.state,
                'category':issue.categ_id.name,
                'task':issue.task_id and self._get_task(issue.task_id) or []
            })
        
        return res
        
    def _get_task(self,task_id):
        pool = pooler.get_pool(self.cr.dbname)
        res=[]
        task = pool.get('project.task').browse(self.cr, self.uid, task_id.id)
        res.append({
        'create_date':task.create_date,
        'date_deadline':task.date_deadline,
        'name':task.name,
        'asigned_to':task.user_id.name,
        'planned_hours':task.planned_hours,
        'remaining_hours':task.remaining_hours,
        'cost':'0',
        'state':task.state,
        })
        return res

report_sxw.report_sxw(
  'report.project.issuereport',
  'project.issue',
  'addons/project_issue_report2/report/project_issue.rml',
  parser=project_issue
)

