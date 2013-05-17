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

    def _project_search(self, cr, uid, obj, name, args, context=None):
        """ Searches Ids of Projects
        @return: Ids of Projects
        """
        cr.execute("""
            select pp.id, tabla2.name
                from
                (
                    select tabla.id, tabla.full_name as name
                        from(
                        Select
                            node.id,node.name AS short_name,
                            cast ((count(parent.name)) as int) as nivel,
                            array_to_string( array_agg( distinct parent.name ), ' / ' ) as full_name
                            from account_analytic_account as node,account_analytic_account  as parent
                            where node.parent_left between parent.parent_left and parent.parent_right
                            group by node.name,node.parent_left,node.id
                            order by node.parent_left)tabla
                        where tabla.full_name """ + str(args[0][1]) + """ '%%%s%%')tabla2
                        join project_project pp
                        on pp.analytic_account_id = tabla2.id """ % (str(args[0][2]),))
        datas = cr.dictfetchall()
        ids = [('id', 'in', [data['id'] for data in datas])]
        return ids

    def _complete_name(self, cr, uid, ids, name, args, context=None):
        return super(project_project, self)._complete_name(cr, uid, ids, name,
                        args, context=context)
    _columns = {
        'complete_name2': fields.function(_complete_name,
                fnct_search=_project_search, string="Project Name",
                type='char', size=250),
    }
