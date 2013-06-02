# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from osv import osv, fields
import time
from account import account
from osv import fields, osv
from lxml import etree
import netsvc
import pooler
from osv.orm import browse_record, browse_null
from tools.translate import _
import base64
import StringIO
import pooler
from time import strftime
import csv
import pprint
from string import upper
from string import join


class wizard_account_diot_mx(osv.osv_memory):

    _name = 'account.diot.report'
    _description = 'Account - DIOT Report for Mexico'
    _columns = {
        'month_id': fields.many2one('account.period', 'Month', help='Select month', required=True),
    }

    def create_diot(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        acc_diot_obj = self.browse(cr, uid, ids, context=context)
        for wiz_qty in self.browse(cr, uid, ids, context=context):
            print "Periodo elegido", wiz_qty.month_id.id
            period_id = wiz_qty.month_id.id
        src = []
        res2 = []
        matrix_row = []
        matrix_col = []
        diot_row = diot_col = []
        lines = []
        untax_amount = 0.0
        iva16 = 0.0
        amount_exe = 0
        inv_obj = pooler.get_pool(cr.dbname).get('account.invoice')
        date_period = pooler.get_pool(cr.dbname).get('account.period').browse(cr, uid, [( int(period_id))])
        print "date_period", date_period
        for line in date_period:
            date_start = line.date_start
            date_stop = line.date_stop
            print date_start, date_stop

        account_invoice = pooler.get_pool(cr.dbname).get('account.invoice').search(cr, uid, [('type','=', 'in_invoice')])

        print 'account_invoice', account_invoice, len(account_invoice)
        counter = 0
        dic_move_line = {}
        for items in account_invoice:
            untax_amount = 0.0
            invo = pooler.get_pool(cr.dbname).get('account.invoice').browse(cr, uid, items, context=context)
            move_lines = invo.payment_ids
            for payment in move_lines:
                if payment.date >= date_start and payment.date <= date_stop:
                    amount_0 = amount_16 = amount_exe = amount_11 = 0
                    print invo.tax_line
                    for tax in invo.tax_line:
                        print "Tax Category", tax.tax_category_id.name
                        if tax.name == 'IVA(16.0%) Purchase':
                            amount_16 = tax.base * ((payment.debit) / ( invo.amount_total))
                            print "amount_16", amount_16
                        if tax.name == 'IVA(11.0%) Purchase':
                            amount_11 = tax.base * ((payment.debit) / ( invo.amount_total))
                            print "amount_11", amount_11
                        if tax.name == 'IVA(0%) Purchase':
                            amount_0 = tax.base * ((payment.debit) / ( invo.amount_total))
                            print "amount_0", amount_0
                        if tax.name == 'IVA( Exento ) Purchase':
                            amount_exe = tax.base * ((payment.debit) / ( invo.amount_total))
                            print "amount_exe", amount_exe
#                        if tax.name == 'IVA( 16% ) Retencion Purchase':
#                            amount_exe = tax.base
#                        if tax.name == 'IVA( 11% ) Retencion  Purchase':
#                            amount_exe = tax.base
#                        if tax.name == 'IVA( 4% ) Retencion  Purchase':
#                            amount_exe = tax.base
                        untax_amount += tax.amount
                    if (str(invo.partner_id.vat)) in dic_move_line:
                        print invo.partner_id.name
                        line_move = dic_move_line[(str(invo.partner_id.vat))]    
                        line_move[7] = line_move[7] + amount_16
                        line_move[8] = line_move[8] + amount_11
                        line_move[9] = line_move[9] + amount_0
                        line_move[10] = line_move[10] + amount_exe
                        dic_move_line [(str(invo.partner_id.vat))] = line_move
                    else:
                        print invo.partner_id.name
                        matrix_row.append(str(invo.partner_id.type_of_third))
                        matrix_row.append(str(invo.partner_id.type_of_operation))
                        matrix_row.append(str(invo.partner_id.vat))
                        if invo.partner_id.type_of_third == "05":
                            if invo.partner_id.number_fiscal_id_diot:
                                matrix_row.append(str(invo.partner_id.number_fiscal_id_diot))
                            else:
                                matrix_row.append("")
                        else:
                            matrix_row.append("")
                        if invo.partner_id.type_of_third != "04":
                            matrix_row.append(str(invo.partner_id.name))
                        else:
                            matrix_row.append("")
                        if invo.partner_id.type_of_third != "04":
                            matrix_row.append(str(invo.partner_id.diot_country))
                        else:
                            matrix_row.append("")
                        if invo.partner_id.type_of_third != "04":
                            matrix_row.append(str(invo.partner_id.nacionality_diot))
                        else:
                            matrix_row.append("")
                        matrix_row.append(amount_16)
                        matrix_row.append(amount_11)
                        matrix_row.append(amount_0)
                        matrix_row.append(amount_exe)
                        dic_move_line [(str(invo.partner_id.vat))] = matrix_row
                    matrix_row = []
        invoice_ids = []
        buf = StringIO.StringIO()
        print "dic", dic_move_line
        for diot in dic_move_line:
            cadena = str(dic_move_line[diot][0]) + '|' + str(dic_move_line[diot][1]) + '|' + str(dic_move_line[diot][2]) + '|' + str(dic_move_line[diot][3]) + '|' + str(dic_move_line[diot][4]) + '|' + str(dic_move_line[diot][5]) + '|' + str(dic_move_line[diot][6]) + '|' + (str(int(round((dic_move_line[diot][7]),0)))) + '||' + (str(int(round((dic_move_line[diot][8]),0)))) + '||||||||' + (str(int(round((dic_move_line[diot][9]),0)))) + '|' + (str(int(round((dic_move_line[diot][10]),0)))) + '||||' + '\n'
            buf.write(upper(cadena))
        out = base64.encodestring(buf.getvalue())
        buf.close()
        period_id =  pooler.get_pool(cr.dbname).get('account.period').browse(cr, uid, period_id)
        filename = "%s-%s.txt" % ("OPENERP-DIOT", strftime('%Y-%m-%d'))
        datas = {'ids' : context.get('active_ids',[])}
        res = self.read(cr, uid, ids, ['time_unit','measure_unit'])
        res = res and res[0] or {}
        datas['form'] = res

        context.update({'filename': filename, 'file': out})
        return {
            'name': 'Delivery Report',
            'view_type': 'form',
            'view_mode': 'form',
            'context': context,
            'res_model': 'account.diot.report.delivery',
            'type': 'ir.actions.act_window',
            'context': context,
            'target': 'new',
            }
wizard_account_diot_mx()

class wizard_account_diot_mx_delivery(osv.osv_memory):

    _name = 'account.diot.report.delivery'
    _description = 'Account DIOT Report for Mexico'
    _columns = {
        'filename': fields.char('Filename', size=128, readonly=True, help='This is Filename'),
        'file': fields.binary('File', readonly=True),
    }

    _defaults = {
        'filename': lambda self, cr, uid, context=None: context and context.get('filename', False),
        'file': lambda self, cr, uid, context=None: context and context.get('file', False),
    }

    def finish_report_diot(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        return
wizard_account_diot_mx_delivery()
