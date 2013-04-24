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


class account_invoice(osv.Model):
    _inherit = 'account.invoice'

    def action_move_create(self, cr, uid, ids, context=None):
        invoice_line_obj = self.pool.get('account.invoice.line')
        account_obj = self.pool.get('account.account')
        for id_ in ids:
            lines = invoice_line_obj.search(
                cr, uid, [('invoice_id', '=', id_)])
            for line in lines:
                id_account = invoice_line_obj.browse(
                    cr, uid, line).account_id.id
                type_line = account_obj.browse(cr, uid, id_account).type
                if type_line == 'receivable' or type_line == 'payable':
                    raise osv.except_osv(_('Error'), _(
                        """Type of account in line's must be differt
                           to 'receivable' and 'payable'"""))
            type_acc_invo = self.browse(cr, uid, id_).account_id.type
            type_invoice = self.browse(cr, uid, id_).type
            if (type_invoice == 'out_invoice' or
                type_invoice == 'out_refound') and \
               type_acc_invo != 'receivable':
                raise osv.except_osv(_('Error'), _(
                    """Type of account in invoice to Customer
                       must be 'receivable'"""))
            if (type_invoice == 'in_invoice' or
               type_invoice == 'in_refound') and \
               type_acc_invo != 'payable':
                raise osv.except_osv(_('Error'), _(
                    "Type of account in invoice to Partner must be 'payable'"))
        return super(account_invoice, self).action_move_create(cr, uid, ids)
