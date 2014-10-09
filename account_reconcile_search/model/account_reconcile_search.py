# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from openerp.osv import osv, fields


class account_move_line(osv.Model):
    _inherit = "account.move.line"

    def _get_reconcile(self, cr, uid, ids, name, unknow_none, context=None):
        res = super(account_move_line, self)._get_reconcile(cr, uid, ids, name, unknow_none, context)
        return res

    def fc(s, c, u, ids, cx):
        return ids

    _columns = {
        'reconcile': fields.function(
            _get_reconcile,
            type='char',
            string='Reconcile Ref',
            store={
                'account.move.line': (fc, ['reconcile_id', 'partial_reconcile_id'], 30),
            },
        ),
    }
