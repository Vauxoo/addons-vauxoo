# coding: utf-8
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    "Nhomar Hernandez <nhomar@vauxoo.com>"
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv

import openerp.workflow as workflow


class AccountJournal(osv.Model):
    _inherit = 'account.journal'
    _columns = {
        'default_interim_account_id': fields.many2one('account.account',
                                                      'Interim Account',
                                                      help="""In banks you probably want send account move
                 lines to a interim account before affect the default
                 debit and credit account who
                 will have the booked
                 balance for this kind of operations, in this field
                 you configure this account."""),
        'default_income_account_id': fields.many2one('account.account',
                                                     'Extra Income Account',
                                                     help="""In banks you probably want as counter part for extra
             banking income money use an specific account in this field
             you can canfigure this account"""),
        'default_expense_account_id': fields.many2one('account.account',
                                                      'Expense Account',
                                                      help="""In banks you probable wants send account move lines to an
             extra account to be able to record account move lines due to bank
             comisions and bank debit notes, in this field you configure this
             account."""),
        'concept_ids': fields.one2many('account.journal.bs.config', 'bsl_id',
                                       'Concept Lines', required=False),
        'moveper_line': fields.boolean('One Move per Line', required=False,
                                       help="""Do you want one move per line or one move per bank
                 statement,True: One Per Line False:
                 One Per bank statement"""),
    }


class AccountJournalBsConfig(osv.Model):
    _name = 'account.journal.bs.config'
    _order = 'sequence asc'
    # logger = netsvc.Logger()

    _columns = {
        'sequence': fields.integer('Label'),
        'bsl_id': fields.many2one('account.journal', 'Journal',
                                  required=False),
        'partner_id': fields.many2one('res.partner', 'Partner',
                                      required=False),
        'account_id': fields.many2one('account.account', 'Account',
                                      required=False),
        'expresion': fields.char('Text To be Compared', size=128,
                                 required=True, readonly=False),
        'name': fields.char('Cancept Label', size=128, required=True,
                            readonly=False),
    }
    _defaults = {
        'sequence': 10,
    }

    def _check_expresion(self, cr, user, ids, context=None):
        """A user defined constraints listed in {_constraints}
        @param cr: cursor to database
        @param user: id of current user
        @param ids: list of record ids on which constraints executes

        @return: return True if all constraints satisfied, False otherwise
        """
        try:
            exp_ = self.browse(cr, user, ids, context=context)[0].expresion
            exp = eval(exp_)
            # self.logger.notifyChannel('Chain. ' + str(exp), netsvc.LOG_DEBUG,
            #                           'Succefully Validated')
            if type(exp) is list:
                return True
            else:
                # self.logger.notifyChannel(
                #     'Chain. ' + str(exp_), netsvc.LOG_ERROR,
                #     'Fail With You must use a list')
                return False
        except Exception, var:
            # self.logger.notifyChannel('Chain. ' + str(exp_),
            #                           netsvc.LOG_ERROR,
            #                           'Fail With %s' % var)
            return False

    _constraints = [
        (_check_expresion, '''Error: La expresion no es lista
        debe quedar algo así:
        ["cadenaA","cadenaB","CadenaC"]
        o es inválida''', ['expresion']),
    ]
