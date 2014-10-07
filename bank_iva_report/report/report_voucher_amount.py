##############################################################################
#
# Copyright (c) 2005-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
import time
from openerp.report import report_sxw
from tools import amount_to_text_en
from numero_a_texto import Numero_a_Texto


class report_voucher_amount(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(report_voucher_amount, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'convert': self.convert,
            'debit': self.debit,
            'credit': self.credit,
            'get_payee': self.get_payee,
            'obt_texto': self.obt_texto,
            'get_vat': self.get_vat,
            'get_invoice': self.get_invoice,
            'get_pagos_anteriores': self.get_pagos_anteriores,
            'get_notas_debi_credi': self.get_notas_debi_credi,
            'get_iva': self.get_iva,
            'get_number': self.get_number,
            'get_name': self.get_name,
        })

    def get_payee(self, voucher):
        voucher_obj = self.pool.get('account.voucher')
        id_voucher_pay_sup = voucher_obj.search(self.cr, self.uid, [
                                                ('voucher_pay_support_id', '=', voucher.id)])[0]
        res = voucher_obj.browse(self.cr, self.uid, id_voucher_pay_sup)
        payee = ""
        if res.payee_id:  # si existe un beneficiario se toma este si no se toma la comania
            payee = voucher.payee_id.name
        else:  # la compania
            payee = res.partner_id.name
            #.upper()
        return payee

    def get_vat(self, voucher):
        voucher_obj = self.pool.get('account.voucher')
        id_voucher_pay_sup = voucher_obj.search(self.cr, self.uid, [
                                                ('voucher_pay_support_id', '=', voucher.id)])[0]
        res = voucher_obj.browse(self.cr, self.uid, id_voucher_pay_sup)
        rif = ""
        if res.payee_id:  # si existe un beneficiario se toma este si no se toma la comania
            rif = " "
        else:  # la compania
            rif = res.partner_id.vat
            rif = rif[3:12]
        return rif

    def obt_texto(self, amount):
        res = Numero_a_Texto(amount)
        return res

    def convert(self, amount, cur):
        amt_en = amount_to_text_en.amount_to_text(amount, 'en', cur)
        return amt_en

    def debit(self, move_ids):
        debit = 0.0
        for move in move_ids:  # self.pool.get('account.move.line').browse(self.cr, self.uid, move_ids):
            debit += move.debit
        return debit

    def credit(self, move_ids):
        credit = 0.0
        for move in move_ids:  # self.pool.get('account.move.line').browse(self.cr, self.uid, move_ids):
            credit += move.credit
        return credit

    # lineas del modelo account_voucher que tienen facturas
    def get_invoice(self, voucher):
        voucher_obj = self.pool.get('account.voucher')
        id_voucher_pay_sup = voucher_obj.search(self.cr, self.uid, [
                                                ('voucher_pay_support_id', '=', voucher.id)])[0]
        voucher_bw = voucher_obj.browse(self.cr, self.uid, id_voucher_pay_sup)
        voucher_line = []
        lines = voucher_bw.line_ids
        for l in lines:
            if l.invoice_id:
                voucher_line.append(l)
        return voucher_line

    # devuelve las lineas de los pagos por cada linea con factura de
    # account_voucher
    def get_pagos_anteriores(self, line):
        lis_line = []
        invoice = line.invoice_id
        b = []
        b.append(line)
        b_set = set(b)
        a = "%s" % line.voucher_id.date
        mes = a[0:2]
        dia = a[3:5]
        ano = a[6:10]
        account_voucher = self.pool.get('account.voucher')
        account_voucher_ids = account_voucher.search(
            self.cr, self.uid, [('date', '<=', line.voucher_id.date)])
        account_voucher_brw = account_voucher.browse(
            self.cr, self.uid, account_voucher_ids)
        for voucher in account_voucher_brw:
            for line in voucher.line_ids:
                if line.invoice_id == invoice:
                    lis_line.append(line)
        c_set = set(lis_line)
        d = list(b_set ^ c_set)
        return d

    def get_notas_debi_credi(self, line):
        list_invoice = []
        invoice = line.invoice_id
        if invoice.type == "out_refund" or invoice.type == "in_refund":
            list_invoice.append(invoice)
        return list_invoice

    def get_iva(self, line):
        invoice = line.invoice_id
        rete_line = self.pool.get('account.wh.iva.line')
        rete_line_ids = rete_line.search(self.cr, self.uid, [
                                         ('invoice_id', '=', invoice.id)])
        rete_line_brw = rete_line.browse(self.cr, self.uid, rete_line_ids)

        return rete_line_brw

    def get_number(self, id_voucher):
        voucher = self.pool.get('account.voucher')
        id_voucher_pay_sup = voucher.search(self.cr, self.uid, [
                                            ('voucher_pay_support_id', '=', id_voucher)])[0]
        res1 = voucher.browse(self.cr, self.uid, id_voucher_pay_sup).number
        res2 = voucher.browse(self.cr, self.uid, id_voucher_pay_sup).state
        res = [res1, res2]
        return res

    def get_name(self, id_voucher):
        res1 = ""
        voucher = self.pool.get('account.voucher')
        id_voucher_pay_sup = voucher.search(self.cr, self.uid, [
                                            ('voucher_pay_support_id', '=', id_voucher.id)])[0]
        res1 = voucher.browse(self.cr, self.uid, id_voucher_pay_sup).name
        return res1

report_sxw.report_sxw(
    'report.cash_amount.iva',
    'voucher.pay.support',
    'addons/bank_iva_report/check/report/report_voucher_amount.rml',
    parser=report_voucher_amount, header=False
)
