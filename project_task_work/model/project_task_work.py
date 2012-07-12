#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Humberto Arocha <hbto@vauxoo.com>           
#    Planified by: Rafael Silva <rsilvam@vauxoo.com>
#    Audited by: Nhomar Hernandez <nhomar@vauxoo.com>
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
################################################################################

import time
from osv import fields, osv
from tools.translate import _

class project_task_work(osv.osv):
    _inherit = 'project.task.work'

    def _get_issue(self, cr, uid, ids, fieldname, arg, context=None):
        if context is None: context = {}
        res = {}
        pi_obj = self.pool.get('project.issue')
        ptw_brws = self.browse(cr, uid, ids, context=context)
        for ptw_brw in ptw_brws:
            pi_ids = ptw_brw.task_id and pi_obj.search(cr, uid, [('task_id','=',ptw_brw.task_id.id)]) or []
            
            res[ptw_brw.id] = pi_ids and pi_ids[0] or []
        return res

    _columns = {
        'project_id':fields.related(
            'task_id',
            'project_id',
            type='many2one',
            relation='project.project',
            readonly=True,
            store = False,
            string = 'Project',
        ),
        'state':fields.selection([  ('done','Collected'),
                                    ('draft', 'Uncollected'),
                                    ('cancel', 'Cancel'),], 
                                    readonly = False, 
                                    required = True, 
                                    string = 'State'),
        'issue_id':fields.function(
            _get_issue,
            method = True,
            type = 'many2one',
            relation='project.issue',
            string = 'Project issue',
            store = {})
    }
    
    _defaults = {
        'state': 'draft',
    }
    
project_task_work()
