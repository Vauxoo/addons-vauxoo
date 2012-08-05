# -*- encoding: utf-8 -*-
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

from osv import osv
from osv import fields
from tools.translate import _

class account_journal(osv.osv):
    _inherit = 'account.journal'
    _columns = {
        'default_interim_account_id':fields.many2one('account.account','Interim Account',
        help="""In banks you probably want send account move lines to a interim 
account before affect the default debit and credit account who will have the booked 
balance for this kind of operations, in this field you configure this account."""),
        'default_income_account_id':fields.many2one('account.account','Extra Income Account',
        help="""In banks you probably want as counter part for extra banking income money 
use an specific account in this field you can canfigure this account"""),
        'default_expense_account_id':fields.many2one('account.account','Expense Account',
        help="""In banks you probable wants send account move lines to an extra account
to be able to record account move lines due to bank comisions and bank debit notes, 
in this field you configure this account."""),
    }

account_journal()
