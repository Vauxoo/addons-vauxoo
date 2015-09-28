# coding: utf-8
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

from openerp.osv import osv
from openerp.tools.translate import _


class AccountMoveLine(osv.osv):
    _inherit = "account.move.line"

    def _check_analytic_required(self, cr, uid, ids, context=None):
        for aml_brw in self.browse(cr, uid, ids, context=context):
            account_brw = aml_brw.account_id
            analytic_brw = aml_brw.analytic_account_id
            if account_brw.user_type.analytic_policy == 'always' and not \
                    analytic_brw:
                raise osv.except_osv(
                    _('Error :'),
                    _('Analytic policy is set to "Always" with account %s "%s"'
                        ' but the analytic account is missing in the account '
                        'move line with label "%s"'
                        % (account_brw.code, account_brw.name, aml_brw.name)))
            elif account_brw.user_type.analytic_policy == 'never' and \
                    analytic_brw:
                raise osv.except_osv(
                    _('Error :'),
                    _('Analytic policy is set to "Never" with account %s "%s" '
                        'but the account move line with label "%s" has an '
                        'analytic account %s "%s".' % (
                            account_brw.code, account_brw.name, aml_brw.name,
                            analytic_brw.code,
                            analytic_brw.name)))
        return True

    _constraints = [
        (_check_analytic_required, 'Analytic Required Policy Violation',
         ['analytic_account_id']),
    ]
