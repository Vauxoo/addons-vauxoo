# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: Vauxoo C.A.
#    Planified by: Nhomar Hernandez
#    Audited by: Vauxoo C.A.
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
##########################################################################

from openerp.osv import osv, fields


class update_analytic(osv.TransientModel):

    _name = 'update.analytic'

    _columns = {
        'sure': fields.boolean('Sure', help="Are sure this operation"),
        'confirm': fields.boolean('Confirm', help="Are sure this operation"),
    }

    def update_analytic(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        issue_obj = self.pool.get('project.issue')
        for wzr_brw in self.browse(cr, uid, ids, context=context):
            if wzr_brw.sure and wzr_brw.confirm:
                if context.get('active_ids'):
                    issue_obj.update_project(cr, uid,
                                             context.get('active_ids'))

        return {'type': 'ir.actions.act_window_close'}
