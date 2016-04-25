# coding: utf-8
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
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


class AccountInvoice(osv.Model):

    """account_invoice
    """
    _inherit = 'account.invoice'
    _columns = {
        'bank_statement_line_ids': fields.many2many(
            'bank.statement.imported.lines',
            'bs_invoice_rel',
            'invoice_id', 'st_id_id',
            'Invoices',
            help="Invoices to be reconciled with this line",
        ),  # TODO: Resolve: We should use date as filter, is a question of POV
    }

    def button_reconcile_bsl(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        res = []
        bsl_obj = self.pool.get('bank.statement.imported.lines')
        bsl_ids = self.browse(cr, uid, ids, context=context)[
            0].bank_statement_line_ids

        res = [bsl_id.id for bsl_id in bsl_ids]
        bsl_obj.button_setinvoice(cr, uid, res, context=context)
        return True

    def button_unreconcile_bsl(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        res = []
        bsl_obj = self.pool.get('bank.statement.imported.lines')
        bsl_ids = self.browse(cr, uid, ids, context=context)[
            0].bank_statement_line_ids

        res = [bsl_id.id for bsl_id in bsl_ids]
        bsl_obj.button_cancel(cr, uid, res, context=context)
        return True
