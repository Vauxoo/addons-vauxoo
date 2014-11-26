# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
############# Credits #########################################################
#    Coded by: Humberto Arocha <hbto@vauxoo.com>
#    Planified by: Humberto Arocha <hbto@vauxoo.com>
#    Audited by: Humberto Arocha <hbto@vauxoo.com>
###############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################


from openerp.osv import fields, osv


class account_analytic_line(osv.Model):

    _inherit = 'account.analytic.line'

    _columns = {
        'split_unit_amount': fields.float('Distributed Quantity', help='This Quantity is equal to percentage times unit_amount'),
    }


class account_move_line(osv.osv):

    _inherit = "account.move.line"

    def create_analytic_lines(self, cr, uid, ids, context=None):
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        res = super(account_move_line, self).create_analytic_lines(cr, uid, ids, context=context)

        for move_line in self.browse(cr, uid, ids, context=context):
            if move_line.analytics_id:
                for al in move_line.analytic_lines:
                    al.write({
                        'split_unit_amount': al.unit_amount * al.percentage / 100,
                    })
        return res
