# -*- encoding: utf-8 -*-
##############################################################################
#
#    Account analytic required module for OpenERP
#    Copyright (C) 2011 Akretion (http://www.akretion.com). All Rights Reserved
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
#    Developped during the Akretion-Camptocamp code sprint of June 2011
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

from osv import fields, osv
from tools.translate import _


class account_account_type(osv.osv):
    _inherit = "account.account.type"

    _columns = {
        'analytic_policy' : fields.selection([
            ('optional', 'Optional'),
            ('always', 'Always'),
            ('never', 'Never')
            ], 'Policy for analytic account', help="Set the policy for analytic accounts : if you select 'Optional', the accountant is free to put an analytic account on an account move line with this type of account ; if you select 'Always', the accountant will get an error message if there is no analytic account ; if you select 'Never', the accountant will get an error message if an analytic account is present."),
    }

    _defaults = {
        'analytic_policy': lambda *a: 'optional',
        }

account_account_type()


class account_move_line(osv.osv):
    _inherit = "account.move.line"

    def check_analytic_required(self, cr, uid, vals, context=None):
        if vals.has_key('account_id'):
            account = self.pool.get('account.account').browse(cr, uid, vals['account_id'], context=context)
            if account.user_type.analytic_policy == 'always' and not vals.get('analytic_account_id', False):
                raise osv.except_osv(_('Error :'), _("Analytic policy is set to 'Always' with account %s '%s' but the analytic account is missing in the account move line with label '%s'." % (account.code, account.name, vals.get('name', False))))
            elif account.user_type.analytic_policy == 'never' and vals.get('analytic_account_id', False):
                cur_analytic_account = self.pool.get('account.analytic.account').read(cr, uid, vals['analytic_account_id'], ['name', 'code'], context=context)
                raise osv.except_osv(_('Error :'), _("Analytic policy is set to 'Never' with account %s '%s' but the account move line with label '%s' has an analytic account %s '%s'." % (account.code, account.name, vals.get('name', False), cur_analytic_account['code'], cur_analytic_account['name'])))
        return True

    def create(self, cr, uid, vals, context=None, check=True):
        self.check_analytic_required(cr, uid, vals, context=context)
        return super(account_move_line, self).create(cr, uid, vals, context=context, check=check)

    def write(self, cr, uid, ids, vals, context=None, check=True, update_check=True):
        self.check_analytic_required(cr, uid, vals, context=context)
        return super(account_move_line, self).write(cr, uid, ids, vals, context=context, check=check, update_check=update_check)

account_move_line()
