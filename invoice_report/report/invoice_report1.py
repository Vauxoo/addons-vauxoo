# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    Info (info@vauxoo.com)
############################################################################
#    Coded by: isaac (isaac@vauxoo.com)
#    Coded by: moylop260 (moylop260@vauxoo.com)
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
from report import report_sxw
import time
import pooler
from dateutil.relativedelta import relativedelta
import datetime


class invoice_report1(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
            super(invoice_report1, self).__init__(cr, uid, name, context=context)
            self.localcontext.update({
                'time': time,
                'get_invoice':self._get_invoice,
                'compute_lines':self.___compute_lines,
                'get_saldo':self._get_saldo,
                'get_total_debe':self._get_total_debe,
                'get_total_haber':self._get_total_haber,
                'get_total_saldo':self._get_total_saldo,
                'get_currency':self._get_currency,
                'get_address':self._get_address,
                'get_mov_sin_fact':self._get_mov_sin_fact,
                'suma_move_debit':self._suma_move_debit,
                'get_total_move_debit':self._get_total_move_debit,
                'suma_move_credit':self._suma_move_credit,
                'get_total_move_credit':self._get_total_move_credit,
                'get_saldo_total_movs':self._get_saldo_total_movs,
                'get_grand_debit':self._get_grand_debit,
                'get_grand_credit':self._get_grand_credit,
                'get_company':self._get_company,
            })
    def _get_company(self,uid):
        print '999999999999999999999999999999999 dentro del get_company',uid
        usr_brw=self.pool.get('res.users').browse(self.cr, self.uid, uid)
        return usr_brw

    def _get_grand_credit(self, credit_move, credit):
        print '****************************************dentro de grand credit el move',credit_move,'credit',credit
        grand_credit = credit_move + credit
        print 'return',grand_credit
        return grand_credit

    def _get_grand_debit(self, debit_move, debit):
        print '****************************************dentro de grand debit el move',debit_move,'credit',debit
        grand_debit = debit_move + debit
        print 'return',grand_debit
        return grand_debit

    def _get_saldo_total_movs(self, debit, credit):
        self.tot_sdo_mov = debit - credit
        return self.tot_sdo_mov

    def _get_total_move_credit(self):
        return self.move_credit

    def _suma_move_credit(self, credit):
        self.move_credit += credit


    def _get_total_move_debit(self):
        return self.move_debit

    def _suma_move_debit(self, debit):
        self.move_debit += debit

    def _get_mov_sin_fact(self, partner_id, date_start, date_end):
        print 'dentro del get_mov sin facturas----------------------'
        query=""" select  id from account_move_line a where partner_id= %s
                and not exists (select '' from account_invoice b where a.move_id=b.move_id)
                and exists (select '' from account_move c where a.move_id = c.id and c.date between '%s' and'%s' )
                and state='valid'
                """%( partner_id, date_start, date_end )
        self.cr.execute( query )
        move_line_ids = [ ml_id[0] for ml_id in self.cr.fetchall() ]
        print 'los movimientos line sin factura son',move_line_ids
        mov_line_obj = self.pool.get('account.move.line')

        move_line_brw= mov_line_obj.browse(self.cr, self.uid, move_line_ids)
        print 'el move line_brw',move_line_brw
        return move_line_brw



    def _get_currency(self,currency_id):
        currency_obj = self.pool.get('res.currency').browse(self.cr, self.uid, currency_id)
        return currency_obj

    def _get_address (self,partner_id):
        print 'dentro del get adrress con partner id',partner_id
        partner_obj = self.pool.get('res.partner')
        partner_address_obj= self.pool.get('res.partner.address')
        address_id = partner_obj.address_get(self.cr, self.uid, partner_id, adr_pref=['default'])['default']
        print 'el address_id es',address_id
        self.address= partner_address_obj.browse(self.cr, self.uid, address_id)
        print 'el  self.address es',self.address
        return self.address

    def _get_saldo(self,monto):
        print '===============entro al monto y el monto es',monto
        print '===============eel self.amount_line es',self.amount_line

        saldo = monto - self.amount_line
        print '==============y el  saldo es',saldo
        self.saldo_final += saldo
        return saldo


    def ___compute_lines(self,inv_id):
        print 'estamos dentro de compute y el inv_id es:',inv_id
        dic = {}
        saldo_tot=0
        for invoice in self.invoice:
            if inv_id == invoice.id:
                print 'dentro del primer for el invoice.id es',invoice.id

                subq="""
                        select b.id-- devuelve los ids de voucher_line correspondientes a esa factura
                            from account_voucher a
                            inner join account_voucher_line b
                                on a.id=b.voucher_id
                                and b.amount<>0
                            inner join account_move_line c
                                on c.id=b.move_line_id
                            inner join account_invoice d
                                on d.move_id=c.move_id
                            where d.id=%s
                            and a.state='posted'
                """%( inv_id)
                self.cr.execute( subq )
                voucher_line_ids = [ vl_id[0] for vl_id in self.cr.fetchall() ]
                print 'los voucher ids de la factura',invoice.id,'son',voucher_line_ids
                vou_obj = self.pool.get('account.voucher.line')
                vou_brw= vou_obj.browse(self.cr, self.uid, voucher_line_ids)
                self.amount_line=0
                for amount_line in vou_brw:
                    self.amount_line += amount_line.amount
                    print '------------el amount es:',amount_line.amount

                self.debe_tot+=invoice.amount_total
        print 'la suma del monto es:',self.amount_line
        print 'el return dentro de compute es',vou_brw
        self.haber_tot+=self.amount_line
        print 'el total del haber es',self.haber_tot
        print 'el total del debe es',self.debe_tot
        return vou_brw

    def _get_invoice(self, partner_id, date_start, date_end, currency_id):
        print 'En get_invoice: partner id es',partner_id,'start',date_start,'end',date_end,'moneda',currency_id
        inv_obj = self.pool.get('account.invoice')
        inv_ids = inv_obj.search(self.cr, self.uid, [('partner_id', '=', partner_id),
                                                     ('state', 'not in', ['cancel', 'proforma2', 'proforma']),
                                                     ('date_invoice', '>=', date_start),
                                                     ('date_invoice', '<=', date_end),
                                                     ('currency_id', '=', currency_id), ] )
        inv_brw= inv_obj.browse(self.cr, self.uid, inv_ids)
        print 'los ids de las facturas son',inv_ids
        #~ print 'lo browse de invoice es',inv_brw.internal_number
        self.invoice=inv_brw
        print 'el inv_brw es',inv_brw
        self.haber_tot = 0
        self.debe_tot = 0
        self.saldo_final = 0
        self.move_debit = 0
        self.move_credit = 0
        return inv_brw

    def _get_total_debe(self):
        return self.debe_tot

    def _get_total_haber(self):
        return self.haber_tot

    def _get_total_saldo(self):
        return self.saldo_final
report_sxw.report_sxw('report.invoice.report1', 'res.partner','addons/invoice_report/report/invoice_report1.rml', parser=invoice_report1,  header="internal landscape")

