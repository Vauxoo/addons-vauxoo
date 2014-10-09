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


from openerp import tools
from openerp.osv import fields, osv


class project_project(osv.Model):

    _inherit = 'project.project'

    def _project_search(self, cr, uid, obj, name, args, context=None):
        """ Searches Ids of Projects
        @return: Ids of Projects
        """
        cr.execute("""
            SELECT pp.id,*
            FROM (
                Select
                    node.id, node.name AS short_name,
                    --cast ((count(parent.name)) as int) as nivel
                    replace( array_to_string( array_agg( parent.name order by parent.nivel asc), ' / ' ), '\n', ' ') as full_name
                from account_analytic_account as node, ( SELECT vw.nivel, account_analytic_account.*
                FROM (
                        Select
                            node.id, node.name AS short_name,
                            cast ((count(parent.name)) as int) as nivel
                            --array_to_string( array_agg( distinct parent.name ), ' / ' ) as full_name
                        from account_analytic_account as node,account_analytic_account  as parent
                        where node.parent_left between parent.parent_left and parent.parent_right
                        group by node.name,node.parent_left,node.id
                        order by node.parent_left
                ) vw
                inner join account_analytic_account
                   ON vw.id = account_analytic_account.id) as parent
                where node.parent_left between parent.parent_left and parent.parent_right
                group by node.name,node.parent_left,node.id
                order by node.parent_left
            ) vw join project_project pp
            on pp.analytic_account_id = vw.id
            WHERE vw.full_name """ + tools.ustr( args[0][1] ) + """ '%%%s%%' """ % ( tools.ustr( args[0][2] ),) )
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

    def name_search(self, cr, user, name='', args=None, operator='ilike',
                    context=None, limit=100):
        if not args:
            args = []
        if name:
            ids = self.search(cr, user, [(
                'complete_name2', '=', name)] + args,
                limit=limit, context=context)
            if not ids:
                ids = set()
                ids.update(self.search(cr, user, args + [(
                    'complete_name2', operator, name)],
                    limit=limit, context=context))
                ids.update(map(lambda a: a[0], super(project_project,
                                                    self).name_search(cr, user,
                                                        name=name, args=args,
                                                        operator=operator,
                                                        context=context,
                                                        limit=limit)))
                ids = list(ids)
        else:
            ids = self.search(cr, user, args, limit=limit, context=context)
        result = self.name_get(cr, user, ids, context=context)
        return result


class project_task(osv.Model):
    _inherit = 'project.task'

    _columns = {
        'project_related_id': fields.related('project_id',
            'analytic_account_id', type='many2one',
            relation='account.analytic.account',
            string='Complete Name Project')
    }
