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
            })
    def ___compute_lines(self):
        print 'estamos dentro de compute'
        result = {}
        dic = {}
        for invoice in self.invoice:
            src = []
            lines = []
            if invoice.move_id:
                for m in invoice.move_id.line_id:
                    temp_lines = []
                    if m.reconcile_id:
                        temp_lines = map(lambda x: x.id, m.reconcile_id.line_id)
                    elif m.reconcile_partial_id:
                        temp_lines = map(lambda x: x.id, m.reconcile_partial_id.line_partial_ids)
                    lines += [x for x in temp_lines if x not in lines]
                    src.append(m.id)

            lines = filter(lambda x: x not in src, lines)
            result[invoice.id] = lines

            subq="""
                    select name,amount,voucher_id
                    from account_voucher_line
                    where voucher_id in(
                                        select id from account_voucher
                                        where move_id in (
                                                        select a.move_id
                                                        from account_move_line a where id in (%s)
                                                        )
                                        )
            """%( ','.join(map(str,result[invoice.id])) )
            self.cr.execute( subq )
            montos=self.cr.fetchall()
            print 'el result desglosado es',invoice.id,'--',result[invoice.id],'montos',montos
            #~ print '--------------los montos son',montos
        print 'el result dentro de compute es',result
        return result

    def _get_invoice(self, partner_id):
        print 'partner id es',partner_id
        inv_obj = self.pool.get('account.invoice')
        inv_ids = inv_obj.search(self.cr, self.uid, [('partner_id', '=', partner_id)])
        inv_brw= inv_obj.browse(self.cr, self.uid, inv_ids)
        print 'los ids de las facturas son',inv_ids
        #~ print 'lo browse de invoice es',inv_brw.internal_number
        self.invoice=inv_brw

        return inv_brw


        #~ subquery = """SELECT period_past.id
                        #~ FROM account_period period_past
                        #~ INNER JOIN
                          #~ (
                            #~ SELECT *
                            #~ FROM account_period
                            #~ WHERE id = %s
                          #~ ) period_current
                        #~ ON period_current.fiscalyear_id = period_past.fiscalyear_id
                         #~ AND period_current.date_start > period_past.date_start
                         #~ AND period_current.date_stop > period_past.date_stop
                    #~ """%( period_start )
                #~ self.cr.execute( subquery )
                #~ period_ids = [ period_id[0] for period_id in self.cr.fetchall() ]

report_sxw.report_sxw('report.invoice.report1', 'res.partner','addons/invoice_report/report/invoice_report1.rml', parser=invoice_report1)

