# -*- encoding: utf-8 -*-
########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
########################################################################
#    Copyright (c) 2013 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
########################################################################
#    Coded by: Luis Ernesto García (ernesto_gm@vauxoo.com)
########################################################################
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
########################################################################

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import SUPERUSER_ID


class inactive_account_wizard(osv.osv_memory):
    _name = 'inactive.account.wizard'

    def get_accounts(self, cr, uid, ids, context=None):
        account_obj = self.pool.get('account.account')
        for data in self.browse(cr, uid, ids):
            for acc in data.account_ids:
                account_ids = account_obj.search(cr, uid, [
                    ('id', 'child_of', acc.id)])
                accounts = account_obj.browse(cr, uid, account_ids)
                for account_children in accounts:
                    self._check_moves(cr, uid, account_children.id,
                                      'write', account_children.name,
                                      context=context)
                    self.pool.get('account.account').write(cr, uid,
                                account_children.id, {'active': False})
        return True

    def _check_moves(self, cr, uid, ids, method, account=None,
                     context=None):
        account_obj = self.pool.get('account.account')
        line_obj = self.pool.get('account.move.line')
        account_ids = account_obj.search(
            cr, SUPERUSER_ID, [('id', 'child_of', ids)])
        if line_obj.search(cr, uid,
                           [('account_id', 'in', account_ids)]):
            if method == 'write':
                raise osv.except_osv(_('Error!'), _(
                    'You cannot deactivate an account '
                    'that contains journal items.'))
            elif method == 'unlink':
                raise osv.except_osv(_('Error!'), _(
                    'You cannot remove an account that '
                    'contains journal items.'))
        # Checking whether the account is set as a property to any
        #~ Partner or not

        value = 'account.account,' + str(ids)
        partner_prop_acc = self.pool.get('ir.property').search(cr,
            uid, [('value_reference', '=', value)], context=context)
        conc_acc = ''
        if account:
            conc_acc = '\nAccount: ' + account
        if partner_prop_acc:
            conc_acc = conc_acc + '\nIds Property:'
            for proper in partner_prop_acc:
                conc_acc = conc_acc + '\n- ' + str(proper)
            raise osv.except_osv(_('Warning!'), _('You cannot '
                'remove/deactivate an account which is set on a '
                'customer or supplier.') + conc_acc)
        return True

    _columns = {
        'account_ids': fields.many2many('account.account',
                                        'account_account_rel',
                                        'account_wizard_id',
                                        'account_id', 'accounts'),
    }
