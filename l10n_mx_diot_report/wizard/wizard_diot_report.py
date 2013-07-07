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

from openerp.osv import osv, fields
import time
from account import account
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
import datetime
from dateutil.relativedelta import *

class wizard_account_diot_mx(osv.osv_memory):

    _name = 'account.diot.report'
    _description = 'Account - DIOT Report for Mexico'
    _columns = {
        'name': fields.char('File Name', readonly=True),
        'company_id' : fields.many2one('res.company', 'Company', required=True),
        #Change name by period
        'month_id': fields.many2one('account.period', 'Period', help='Select period', required=True),
        'filename': fields.char('File name', size=128, readonly=True, help='This is File name'),
        'file': fields.binary('File', readonly=True),
        'state': fields.selection([('choose', 'choose'), ('get', 'get')]),

    }

    _defaults = { 
        'state': 'choose',
    }
    
    def create_diot(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        acc_move_line_obj = self.pool.get('account.move.line')
        acc_tax_obj = self.pool.get('account.tax')
        acc_tax_category_obj = self.pool.get('account.tax.category')
        this = self.browse(cr, uid, ids)[0]
        period = this.month_id
        matrix_row = []
        untax_amount = 0.0
        amount_exe = 0
        category_iva_id = acc_tax_category_obj.search(cr, uid, [('name', 'in', ('IVA', 'IVA-EXENTO', 'IVA-RET'))], context=context)
        tax_purchase_ids = acc_tax_obj.search(cr, uid, [('type_tax_use', '=', 'purchase'), ('tax_category_id', 'in', category_iva_id)], context=context)
        move_lines_diot = acc_move_line_obj.search(cr, uid, [('period_id', '=', period.id), ('tax_id_secundary', 'in', tax_purchase_ids)])
        dic_move_line = {}
        move_not_amount = []
        partner_ids = []
        for items in acc_move_line_obj.browse(cr, uid, move_lines_diot, context=context):
            if items.partner_id.vat_split == False:
                partner_ids.append(items.partner_id.id)
        
        if partner_ids:
            return {
                'name': 'Suppliers without RFC',
                'view_type' : 'form',
                'view_mode': 'tree,form',
                'res_model': 'res.partner',
                'type': 'ir.actions.act_window',
                'domain': [('id', 'in', partner_ids), '|',('active', '=', False), ('active', '=', True)],
            }
        
        for line in acc_move_line_obj.browse(cr, uid, move_lines_diot, context=context):
            if line.partner_id.vat_split == False:
                raise osv.except_osv(('Error !'), ('Missing field (VAT) : "%s"') % (line.partner_id.name))
            if line.partner_id.type_of_third == False:
                raise osv.except_osv(('Error !'), ('Missing field (type of third) : "%s"') % (line.partner_id.name))
            if line.partner_id.type_of_operation == False:
                raise osv.except_osv(('Error !'), ('Missing field (type of operation) : "%s"') % (line.partner_id.name))
            if line.partner_id.type_of_third == '05' and line.partner_id.diot_country == False:
                raise osv.except_osv(('Error !'), ('Missing field (DIOT Country) : "%s"') % (line.partner_id.name))
                
            if line.date >= period.date_start and line.date <= period.date_stop:
                amount_0 = amount_16 = amount_exe = amount_11 = amount_ret = 0
                if line.tax_id_secundary.tax_category_id.name == 'IVA' and line.tax_id_secundary.amount == 0.16:
                    amount_16 = line.amount_base
                if line.tax_id_secundary.tax_category_id.name == 'IVA' and line.tax_id_secundary.amount == 0.11:
                    amount_11 = line.amount_base
                if line.tax_id_secundary.tax_category_id.name == 'IVA' and line.tax_id_secundary.amount == 0:
                    amount_0 = line.amount_base
                if line.tax_id_secundary.tax_category_id.name == 'IVA-EXENTO' and line.tax_id_secundary.amount == 0:
                    amount_exe = line.amount_base
                if line.tax_id_secundary.tax_category_id.name == 'IVA-RET':
                    amount_ret = line.amount_base
                #Checar monto
                untax_amount += line.amount_base
                if line.partner_id.vat_split in dic_move_line:
                    line_move = dic_move_line[line.partner_id.vat_split]    
                    line_move[7] = line_move[7] + amount_16
                    line_move[8] = line_move[8] + amount_11
                    line_move[9] = line_move[9] + amount_0
                    line_move[10] = line_move[10] + amount_exe
                    line_move[11] = line_move[11] + amount_ret
                    dic_move_line.update({line.partner_id.vat_split : line_move})
                else:
                    matrix_row.append(line.partner_id.type_of_third)
                    matrix_row.append(line.partner_id.type_of_operation)
                    matrix_row.append(line.partner_id.vat_split)

                    if line.partner_id.type_of_third == "05" and line.partner_id.number_fiscal_id_diot != False:
                        matrix_row.append(line.partner_id.number_fiscal_id_diot)
                    else:
                        matrix_row.append("")
                    if line.partner_id.type_of_third != "04":
                        matrix_row.append(line.partner_id.name)
                        matrix_row.append(line.partner_id.diot_country)
                        if line.partner_id.nacionality_diot != False:
                            matrix_row.append(line.partner_id.nacionality_diot)
                        else:
                            matrix_row.append("")
                    else:
                        matrix_row.append("")
                        matrix_row.append("")
                        matrix_row.append("")
                    matrix_row.append(amount_16)
                    matrix_row.append(amount_11)
                    matrix_row.append(amount_0)
                    matrix_row.append(amount_exe)
                    matrix_row.append(amount_ret)
                    dic_move_line.update({line.partner_id.vat_split : matrix_row})
                matrix_row = []
        buf = StringIO.StringIO()
        for diot in dic_move_line:
            #~ cadena = dic_move_line[diot][0] + '|' + dic_move_line[diot][1] + '|' + dic_move_line[diot][2] + '|' + dic_move_line[diot][3] + '|' + dic_move_line[diot][4] + '|' + dic_move_line[diot][5] + '|' + dic_move_line[diot][6] + '|' + round((dic_move_line[diot][7]),0) + '||' + round((dic_move_line[diot][8]),0) + '|||||||||' + round((dic_move_line[diot][9]),0) + '|' + round((dic_move_line[diot][10]),0) + '|' + round((dic_move_line[diot][11]),0) + '||' + '\n'
            cadena = str(dic_move_line[diot][0]) + '|' + str(dic_move_line[diot][1]) + '|' + str(dic_move_line[diot][2]) + '|' + str(dic_move_line[diot][3]) + '|' + str(dic_move_line[diot][4]) + '|' + str(dic_move_line[diot][5]) + '|' + str(dic_move_line[diot][6]) + '|' + (str(int(round((dic_move_line[diot][7]),0)))) + '||' + (str(int(round((dic_move_line[diot][8]),0)))) + '|||||||||' + (str(int(round((dic_move_line[diot][9]),0)))) + '|' + (str(int(round((dic_move_line[diot][10]),0)))) + '|' + (str(int(round((dic_move_line[diot][11]),0)))) + '||' + '\n'
            buf.write(upper(cadena))
        out = base64.encodestring(buf.getvalue())
        buf.close()
        #Revisar estos datos
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
                    

