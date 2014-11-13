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


class account_move_line(osv.Model):
    _inherit = 'account.move.line'

    _columns = {
        'amount_base': fields.float('Amount Base', help='Amount base '
            'without amount tax'),
        'tax_id_secondary': fields.many2one('account.tax', 'Tax Secondary',
            help='Tax used for this move'),
        'not_move_diot': fields.boolean('Not Consider in Diot', help='If'
            ' this field is active, although of this item have data for DIOT,'
            ' not be considered.'),
    }

    def onchange_tax_secondary(self, cr, uid, ids, account_id=False, context=None):
        acc_tax_obj = self.pool.get('account.tax')
        tax_acc = acc_tax_obj.search(cr, uid, [
            ('account_paid_voucher_id', '=', account_id)], context=context)
        if tax_acc:
            return {'value': {'tax_id_secondary': tax_acc[0]}}
        else:
            return {'value': {}}

    def write(self, cr, uid, ids, vals, context=None, check=True, update_check=True):
        if context is None:
            context = {}
        if not ids:
            return True
        if isinstance(ids, (int, long)):
            ids = [ids]

        res = super(account_move_line, self).write(cr, uid, ids, vals,
            context=context, check=check, update_check=update_check)
        for line in self.browse(cr, uid, ids, context=context):
            if line.tax_id_secondary and line.tax_id_secondary.type_tax_use == 'purchase':
                cat_tax = line.tax_id_secondary.tax_category_id
                if cat_tax and cat_tax.name in ('IVA', 'IVA-EXENTO') and line.amount_base <= 0 and\
                        not line.not_move_diot:
                    raise osv.except_osv(_('Warning!'), _('The lines with tax of purchase, need '
                        'have a value in the amount base.'))
                elif cat_tax and cat_tax == 'IVA-RET' and line.credit <= 0 and\
                        not line.not_move_diot:
                    raise osv.except_osv(_('Warning!'), _('The lines with tax of purchase, need '
                        'have a value in the credit.'))
        return res

    def onchange_account_id(self, cr, uid, ids, account_id=False, partner_id=False, context=None):
        res = super(account_move_line, self).onchange_account_id(cr, uid, ids, account_id, partner_id, context=context)
        acc_tax_obj = self.pool.get('account.tax')
        tax_acc = acc_tax_obj.search(cr, uid, [
            ('account_paid_voucher_id', '=', account_id)], context=context)
        if tax_acc:
            res['value'].update({'tax_id_secondary': tax_acc[0]})
        return res


class account_invoice_tax(osv.Model):
    _inherit = "account.invoice.tax"

    def move_line_get(self, cr, uid, invoice_id, context=None):
        res = []
        super(account_invoice_tax, self).move_line_get(cr, uid, invoice_id)
        tax_invoice_ids = self.search(cr, uid, [
            ('invoice_id', '=', invoice_id)], context=context)
        for inv_t in self.browse(cr, uid, tax_invoice_ids, context=context):
            if not inv_t.amount and not inv_t.tax_code_id and not inv_t.tax_amount:
                continue
            res.append({
                'type': 'tax',
                'name': inv_t.name,
                'price_unit': inv_t.amount,
                'quantity': 1,
                'price': inv_t.amount or 0.0,
                'account_id': inv_t.account_id.id or False,
                'tax_code_id': inv_t.tax_code_id.id or False,
                'tax_amount': inv_t.tax_amount or False,
                'account_analytic_id': inv_t.account_analytic_id.id or False,
                'amount_base': inv_t.base_amount or 0.0,
                'tax_id_secondary': inv_t.tax_id.id or False,
            })
        return res


class account_invoice(osv.Model):
    _inherit = 'account.invoice'

    def line_get_convert(self, cr, uid, value, part, date, context=None):
        res = super(account_invoice, self).line_get_convert(cr, uid, value, part,
            date, context=context)
        res.update({
            'amount_base': value.get('amount_base', False),
            'tax_id_secondary': value.get('tax_id_secondary', False),
        })
        return res
