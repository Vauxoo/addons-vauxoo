# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-today OpenERP SA (<http://www.openerp.com>)
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
##############################################################################

from datetime import datetime, date
from lxml import etree
import time

from openerp import SUPERUSER_ID
from openerp import tools
from openerp.osv import fields, osv
from openerp.tools.translate import _


class project_project(osv.Model):

    _inherit = 'project.project'

    def _get_projects(self, cr, uid, ids, context=None):
        project_project_obj = self.pool.get('project.project')
        return project_project_obj.search(cr, uid,
                                        [('analytic_account_id', '=', ids[0])])

    def action_projects(self, cr, uid, context=None):
        project_ids = self.search(cr, uid, [])
        for project in self.browse(cr, uid, project_ids, context=context):
            self.write(cr, uid, [project.id], {'name': project.name})
        return True

    def _get_parent_id(self, cr, uid, ids, name, args, context=None):
        res = {}
        for project in self.browse(cr, uid, ids, context=context):
            project_parent_id = self.search(cr, uid, [(
                'analytic_account_id', '=', project.parent_id.id)])
            res[project.id] = project_parent_id and project_parent_id[
                0] or None
        return res

    _columns = {
        'parent_id2': fields.function(_get_parent_id, type='many2one',
            relation='project.project',
            string='Parent Project',
            store={
               'account.analytic.account':
                (_get_projects, ['parent_id', 'name'], 10)}, select=2),
        'child_ids2': fields.one2many('project.project',
            'parent_id2', 'Child Accounts'),

    }
