# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Luis Torres (luis_t@vauxoo.com)
############################################################################
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
from openerp.tools.translate import _


class account_account(osv.Model):
    _inherit = 'account.account'

    _columns = {
        'analytic_required': fields.boolean('Analytic Required'),
    }


class account_move(osv.Model):
    _inherit = 'account.move'

    def button_validate(self, cursor, user, ids, context=None):
        account_move_obj = self.pool.get('account.move.line')
        account_obj = self.pool.get('account.account')
        moves = account_move_obj.search(cursor, user, [('move_id', 'in', ids)])
        if moves:
            for move_id in moves:
                move = account_move_obj.browse(cursor, user, move_id)
                name_move = move.name or ''
                analytic_st = move.account_id and move.account_id.analytic_required or False
                if analytic_st is True:
                    account_move_id = move.account_id and move.account_id.id or False
                    analytic_acc_move = move.analytic_account_id and move.analytic_account_id.id or False
                    if analytic_acc_move is False:
                        raise osv.except_osv(_('Error'), _(
                            'Need add analytic account in move whit name ' + name_move + '.'))
        res = super(account_move, self).button_validate(
            cursor, user, ids, context=context)
        return res
