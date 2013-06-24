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
        'name': fields.char('File Name', readonly=True),
        'company_id' : fields.many2one('res.company', 'Company', required=True),
        'month_id': fields.many2one('account.period', 'Month', help='Select month', required=True),
        'filename': fields.char('Filename', size=128, readonly=True, help='This is Filename'),
        'file': fields.binary('File', readonly=True),
        'state': fields.selection([('choose', 'choose'), ('get', 'get')]),

    }

    _defaults = { 
        'state': 'choose',
    }


    def create_diot(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids)[0]
        if context is None:
            context = {}
        acc_diot_obj = self.browse(cr, uid, ids, context=context)
        for wiz_qty in self.browse(cr, uid, ids, context=context):
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
        for line in date_period:
            date_start = line.date_start
            date_stop = line.date_stop

        account_invoice = pooler.get_pool(cr.dbname).get('account.invoice').search(cr, uid, [('type','=', 'in_invoice')])

        counter = 0
        dic_move_line = {}
        for items in account_invoice:
            untax_amount = 0.0
            invo = pooler.get_pool(cr.dbname).get('account.invoice').browse(cr, uid, items, context=context)
####################    Verify Data  ############################################################################################
            if invo.partner_id.vat == False:
                raise osv.except_osv(('Error !'), ('Missing field (VAT) : "%s"') % (invo.partner_id.name))
            if invo.partner_id.type_of_third == False:
                raise osv.except_osv(('Error !'), ('Missing field (type of third) : "%s"') % (invo.partner_id.name))
            if invo.partner_id.type_of_operation == False:
                raise osv.except_osv(('Error !'), ('Missing field (type of operation) : "%s"') % (invo.partner_id.name))
            if invo.partner_id.type_of_third == '05' and invo.partner_id.diot_country == False:
                raise osv.except_osv(('Error !'), ('Missing field (DIOT Country) : "%s"') % (invo.partner_id.name))

            move_lines = invo.payment_ids
            for payment in move_lines:
                if payment.date >= date_start and payment.date <= date_stop:
                    amount_0 = amount_16 = amount_exe = amount_11 = amount_ret = 0
                    print invo.tax_line
                    for tax in invo.tax_line:
                        if tax.tax_id.tax_category_id.name == 'IVA' and tax.tax_id.amount == 0.16:
                            amount_16 = tax.base * ((payment.debit) / ( invo.amount_total))
                            print "amount_16", amount_16
                        if tax.tax_id.tax_category_id.name == 'IVA' and tax.tax_id.amount == 0.11:
                            amount_11 = tax.base * ((payment.debit) / ( invo.amount_total))
                            print "amount_11", amount_11
                        if tax.tax_id.tax_category_id.name == 'IVA' and tax.tax_id.amount == 0:
                            amount_0 = tax.base * ((payment.debit) / ( invo.amount_total))
                            print "amount_0", amount_0
                        if tax.tax_id.tax_category_id.name == 'IVA-EXENTO' and tax.tax_id.amount == 0:
                            amount_exe = tax.base * ((payment.debit) / ( invo.amount_total))
                            print "amount_exe", amount_exe
                        if tax.tax_id.tax_category_id.name == 'IVA-RET':
                            amount_ret = tax.base * ((payment.debit) / ( invo.amount_total))
                            print "amount_ret", amount_ret
                        untax_amount += tax.amount
                    if (str(invo.partner_id.vat)) in dic_move_line:
                        print invo.partner_id.name
                        line_move = dic_move_line[(str(invo.partner_id.vat))]    
                        line_move[7] = line_move[7] + amount_16
                        line_move[8] = line_move[8] + amount_11
                        line_move[9] = line_move[9] + amount_0
                        line_move[10] = line_move[10] + amount_exe
                        line_move[11] = line_move[11] + amount_ret
                        dic_move_line [(str(invo.partner_id.vat_split))] = line_move
                    else:
                        matrix_row.append(str(invo.partner_id.type_of_third))
                        matrix_row.append(str(invo.partner_id.type_of_operation))
                        matrix_row.append(str(invo.partner_id.vat_split))


                        if invo.partner_id.type_of_third == "05":
                            if invo.partner_id.number_fiscal_id_diot != False:
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
                            if invo.partner_id.nacionality_diot != False:
                                matrix_row.append(str(invo.partner_id.nacionality_diot))
                            else:
                                matrix_row.append("")
                        else:
                            matrix_row.append("")
                        matrix_row.append(amount_16)
                        matrix_row.append(amount_11)
                        matrix_row.append(amount_0)
                        matrix_row.append(amount_exe)
                        matrix_row.append(amount_ret)
                        dic_move_line [(str(invo.partner_id.vat))] = matrix_row
                    matrix_row = []
        invoice_ids = []
        buf = StringIO.StringIO()
        print "dic", dic_move_line
        for diot in dic_move_line:
            cadena = str(dic_move_line[diot][0]) + '|' + str(dic_move_line[diot][1]) + '|' + str(dic_move_line[diot][2]) + '|' + str(dic_move_line[diot][3]) + '|' + str(dic_move_line[diot][4]) + '|' + str(dic_move_line[diot][5]) + '|' + str(dic_move_line[diot][6]) + '|' + (str(int(round((dic_move_line[diot][7]),0)))) + '||' + (str(int(round((dic_move_line[diot][8]),0)))) + '|||||||||' + (str(int(round((dic_move_line[diot][9]),0)))) + '|' + (str(int(round((dic_move_line[diot][10]),0)))) + '|' + (str(int(round((dic_move_line[diot][11]),0)))) + '||' + '\n'
            buf.write(upper(cadena))
        out = base64.encodestring(buf.getvalue())
        buf.close()
        period_id =  pooler.get_pool(cr.dbname).get('account.period').browse(cr, uid, period_id)
        this.name = "%s-%s.txt" % ("OPENERP-DIOT", strftime('%Y-%m-%d'))
        datas = {'ids' : context.get('active_ids',[])}
        res = self.read(cr, uid, ids, ['time_unit','measure_unit'])
        res = res and res[0] or {}
        datas['form'] = res

        self.write(cr, uid, ids, {'state': 'get',
                                  'file': out,
                                  'filename':this.name
                                    }, context=context)

        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': this.id,
            'views': [(False, 'form')],
            'res_model': 'account.diot.report',
            'target': 'new',
            }

wizard_account_diot_mx()


