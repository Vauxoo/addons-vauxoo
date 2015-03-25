# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Hugo Francisco Adan Oliva(hugo@vauxoo.com)
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

from openerp.osv import fields, osv
from openerp.tools.translate import _


class AccountInvoice(osv.Model):
    _inherit = 'account.invoice'

    def get_states(self, cr, uid, context):
        return [
            ('draft', 'Draft'),
            ('proforma', 'Pro-forma'),
            ('proforma2', 'Pro-forma'),
            ('validate', _('By validating')),
            ('open', 'Open'),
            ('paid', 'Paid'),
            ('cancel', 'Cancelled'), ]

    _columns = {
        'state': fields.selection(
            get_states,
            'Status', select=True, readonly=True,
            track_visibility='onchange',
            help=' * The \'Draft\' status is used when a user is \
            encoding a new and unconfirmed Invoice. \
            * The \'By validating\' status is used when an invoice is \
            ready to be validate. \
            \n* The \'Pro-forma\' when invoice is in Pro-forma \
            status,invoice does not have an invoice number. \
            \n* The \'Open\' status is used when user create invoice,\
            a invoice number is generated.Its in open status till user \
            does not pay invoice. \
            \n* The \'Paid\' status is set automatically when the invoice \
            is paid. Its related journal entries may or may not be reconciled.\
            \n* The \'Cancelled\' status is used when user cancel invoice.')}
