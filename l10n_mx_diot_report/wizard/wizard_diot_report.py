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
from tools.translate import _
import base64
import pooler
from time import strftime
from string import upper
from string import join
import datetime
import tempfile
import os
from dateutil.relativedelta import *
import csv


class wizard_account_diot_mx(osv.osv_memory):

    _name = 'account.diot.report'
    _description = 'Account - DIOT Report for Mexico'
    _columns = {
        'name': fields.char('File Name', readonly=True),
        'company_id': fields.many2one('res.company', 'Company',
            required=True),
        'period_id': fields.many2one('account.period', 'Period',
            help='Select period', required=True),
        'filename': fields.char('File name', size=128, readonly=True,
            help='This is File name'),
        'filename_csv': fields.char('File name', size=128, readonly=True),
        'file': fields.binary('File', readonly=True, help='This file, you can import the SAT'),
        'file_csv': fields.binary('File', readonly=True, help='It will open in your program office, to validate numbers'),
        'state': fields.selection([('choose', 'Choose'), ('get', 'Get'),
            ('not_file', 'Not File')]),
        'entries_to_print': fields.selection([('all', 'All Entries'),
            ('posted', 'Posted Entries')], 'Entries to show', required=True)
    }

    _defaults = {
        'state': 'choose',
        'entries_to_print' : 'all'
    }

    def default_get(self, cr, uid, fields, context=None):
        """
        This function load in the wizard, the company used by the user, and
        the previous period to the current
        """
        if context is None:
            context = {}
        data = super(wizard_account_diot_mx, self).default_get(cr, uid,
            fields, context=context)
        time_now = datetime.date.today()+relativedelta(months=-1)
        company_id = self.pool.get('res.company')._company_default_get(cr, uid,
            'account.diot.report', context=context)
        period_id = self.pool.get('account.period').search(cr, uid,
            [('date_start', '<=', time_now),
            ('date_stop', '>=', time_now),
            ('company_id', '=', company_id)])
        if period_id:
            data.update({'company_id': company_id,
                        'period_id': period_id[0]})
        return data

    def create_diot(self, cr, uid, ids, context=None):
        """
        This function create the file for report to DIOT, take the amount base
        paid by partner in each tax, in the period and company selected.
        """
        if context is None:
            context = {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        acc_move_line_obj = self.pool.get('account.move.line')
        acc_tax_obj = self.pool.get('account.tax')
        acc_tax_category_obj = self.pool.get('account.tax.category')
        this = self.browse(cr, uid, ids)[0]
        period = this.period_id
        matrix_row = []
        amount_exe = 0
        partner_company_id = this.company_id.partner_id.id
        category_iva_ids = acc_tax_category_obj.search(cr, uid, [
            ('name', 'in', ('IVA', 'IVA-EXENTO', 'IVA-RET', 'IVA-PART'))], context=context)
        tax_purchase_ids = acc_tax_obj.search(cr, uid, [
            ('type_tax_use', '=', 'purchase'),
            ('tax_category_id', 'in', category_iva_ids)], context=context)
        account_ids_tax = []
        for tax in acc_tax_obj.browse(cr, uid, tax_purchase_ids, context=context):
            account_ids_tax.append(tax.account_paid_voucher_id.id)
        attrs = [
            ('period_id', '=', period.id),
            ('partner_id', '!=', partner_company_id),
            ('tax_id_secondary', 'in', tax_purchase_ids),
            ('state', '=', 'valid'),
            ('account_id', 'in', account_ids_tax),
            ('not_move_diot', '=', False)]
        if this.entries_to_print == 'posted':
            attrs.append(('move_id.state', '=', 'posted'))
        move_lines_diot = acc_move_line_obj.search(cr, uid, attrs, context=context)
        dic_move_line = {}
        partner_ids_to_fix = []
        moves_without_partner = []
        moves_amount_0 = []
        for items in acc_move_line_obj.browse(cr, uid, move_lines_diot,
            context=context):
            if not items.partner_id:
                moves_without_partner.append(items.id)
        if moves_without_partner:
            return {
                'name': 'Moves without supplier',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.move.line',
                'type': 'ir.actions.act_window',
                'domain': [('id', 'in', moves_without_partner), ],
            }
        lines_difference_in_amount = []
        for line in acc_move_line_obj.browse(cr, uid, move_lines_diot,
            context=context):
            partner_id = line.partner_id
            partner_vat = upper((partner_id.vat_split or '').replace('-', '')
                                .replace('_', '').replace(' ', ''))
            if not partner_vat \
                or not partner_id.type_of_third\
                or not partner_id.type_of_operation\
                or (partner_id.type_of_third == '05'
                    and not partner_id.diot_country)\
                or (partner_id.type_of_third == '04' and
                    not self.pool.get('res.partner').check_vat_mx(partner_vat)):
                partner_ids_to_fix.append(partner_id.id)
            if partner_ids_to_fix:
                continue
            if line.date >= period.date_start and line.date <= period.date_stop:
                amount_0 = amount_16 = amount_exe = amount_11 = amount_ret = 0
                amount_base_tax = line.amount_base or 0
                if line.credit:
                    amount_base_tax = amount_base_tax * -1
                category = line.tax_id_secondary.tax_category_id.name or False
                amount_base = line.tax_id_secondary.amount or 0
                line_diot = False
                if (category == 'IVA' and amount_base in [0.16, 0.11, 0]) or\
                    (category == 'IVA-EXENTO' and amount_base == 0) or category == 'IVA-RET':
                    line_diot = True
                if category in ('IVA', 'IVA-PART') and amount_base == 0.16 or\
                    line.tax_id_secondary.tax_diot == 'tax_16' and line_diot == False:
                    amount_16 = amount_base_tax or 0
                if category == 'IVA' and amount_base == 0.11 or\
                    line.tax_id_secondary.tax_diot == 'tax_11' and line_diot == False:
                    amount_11 = amount_base_tax or 0
                if category == 'IVA' and amount_base == 0 or\
                    line.tax_id_secondary.tax_diot == 'tax_0' and line_diot == False:
                    amount_0 = amount_base_tax or 0
                if category == 'IVA-EXENTO' and amount_base == 0 or\
                    line.tax_id_secondary.tax_diot == 'tax_exe' and line_diot == False:
                    amount_exe = amount_base_tax or 0
                if category == 'IVA-RET' or line.tax_id_secondary.tax_diot == 'tax_ret' and\
                    line_diot == False:
                    amount_ret = line.credit or line.debit*-1 or 0
                if amount_0 + amount_16 + amount_exe + amount_11 + amount_ret == 0:
                    moves_amount_0.append(line.id)
                if partner_vat in dic_move_line:
                    line_move = dic_move_line[partner_vat]
                    line_move[7] = line_move[7] + amount_16
                    line_move[8] = line_move[8] + amount_11
                    line_move[9] = line_move[9] + amount_0
                    line_move[10] = line_move[10] + amount_exe
                    line_move[11] = line_move[11] + amount_ret
                    dic_move_line.update({
                        partner_vat: line_move})
                else:
                    matrix_row.append(line.partner_id.type_of_third)
                    matrix_row.append(line.partner_id.type_of_operation)
                    matrix_row.append(partner_vat)
                    if line.partner_id.type_of_third == "05" and\
                        line.partner_id.number_fiscal_id_diot:
                        matrix_row.append(
                            line.partner_id.number_fiscal_id_diot)
                    else:
                        matrix_row.append("")
                    if line.partner_id.type_of_third != "04":
                        matrix_row.append(line.partner_id.name)
                        matrix_row.append(line.partner_id.diot_country)
                        if line.partner_id.nacionality_diot:
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
                    dic_move_line.update({
                        partner_vat: matrix_row})
                matrix_row = []
                if category and category in ('IVA', 'IVA-EXENTO') and line.tax_id_secondary.amount != 0:
                    amount_line = (line.debit or line.credit) /\
                    (line.tax_id_secondary.tax_category_id.value_tax or\
                    line.tax_id_secondary.amount)
                    difference_amount = abs(amount_line) - abs(amount_base_tax)
                    if abs(difference_amount) > 0.2:
                        lines_difference_in_amount.append(line.id)
        if partner_ids_to_fix:
            return {
                'name': 'Suppliers do not have the information necessary'
                'for the DIOT',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'res.partner',
                'type': 'ir.actions.act_window',
                'domain': [('id', 'in', partner_ids_to_fix), '|', (
                    'active', '=', False), ('active', '=', True)],
            }
        (fileno, fname) = tempfile.mkstemp('.txt', 'tmp')
        if lines_difference_in_amount:
            return {
                'name': 'Movements with differences in amount base',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.move.line',
                'type': 'ir.actions.act_window',
                'domain': [('id', 'in', lines_difference_in_amount)],
            }
        if moves_amount_0:
            return {
                'name': 'Movements to corroborate the amounts of taxes',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.move.line',
                'type': 'ir.actions.act_window',
                'domain': [('id', 'in', moves_amount_0)],
            }
        os.close(fileno)
        f_write = open(fname, 'wb')
        fcsv = csv.DictWriter(f_write, 
            ['type_of_third', 'type_of_operation',
            'vat', 'number_id_fiscal', 'foreign_name',
            'country_of_residence', 'nationality',
            'value_of_acts_or_activities_paid_at_the_rate_of_16%',
            'value_of_acts_or_activities_paid_at_the_rate_of_15%',
            'amount_of_non-creditable_VAT_paid_at_the_rate_of_16%',
            'value_of_acts_or_activities_paid_at_the_rate_of_11%_VAT',
            'value_of_acts_or_activities_paid_at_the_rate_of_10%_VAT',
            'amount_of_non-creditable_VAT_paid_at_the_rate_of_11%',
            'value_of_acts_or_activities_paid_on_import_of_goods_and_'
            'services_at_the_rate_of_16%_VAT',
            'amount_of_non-creditable_VAT_paid_by_imports_at_the_rate_of_16%',
            'value_of_acts_or_activities_paid_on_import_of_goods_and_'
            'services_at_the_rate_of_11%_VAT',
            'amount_of_non-creditable_VAT_paid_by_imports_at_the_rate_of_11%',
            'value_of_acts_or_activities_paid_on_import_of_goods_and_'
            'services_for_which_VAT_is_not_pay_(exempt)',
            'value_of_the_other_acts_or_activities_paid_at_the_rate_of_0%_VAT',
            'value_of_acts_or_activities_paid_by_those_who_do_not_pay_the_'
            'VAT_(Exempt)',
            'tax Withheld by the taxpayer',
            'VAT for returns, discounts and rebates on purchases',
            'show_pipe', ], delimiter='|')
        
        (fileno, fname_csv) = tempfile.mkstemp('.csv', 'tmp_csv')
        os.close(fileno)
        f_write_csv = open(fname_csv, 'wb')
        fcsv_csv = csv.DictWriter(f_write_csv, 
            ['type_of_third', 'type_of_operation',
            'vat', 'number_id_fiscal', 'foreign_name',
            'country_of_residence', 'nationality',
            'value_of_acts_or_activities_paid_at_the_rate_of_16%',
            'value_of_acts_or_activities_paid_at_the_rate_of_15%',
            'amount_of_non-creditable_VAT_paid_at_the_rate_of_16%',
            'value_of_acts_or_activities_paid_at_the_rate_of_11%_VAT',
            'value_of_acts_or_activities_paid_at_the_rate_of_10%_VAT',
            'amount_of_non-creditable_VAT_paid_at_the_rate_of_11%',
            'value_of_acts_or_activities_paid_on_import_of_goods_and_'
            'services_at_the_rate_of_16%_VAT',
            'amount_of_non-creditable_VAT_paid_by_imports_at_the_rate_of_16%',
            'value_of_acts_or_activities_paid_on_import_of_goods_and_'
            'services_at_the_rate_of_11%_VAT',
            'amount_of_non-creditable_VAT_paid_by_imports_at_the_rate_of_11%',
            'value_of_acts_or_activities_paid_on_import_of_goods_and_'
            'services_for_which_VAT_is_not_pay_(exempt)',
            'value_of_the_other_acts_or_activities_paid_at_the_rate_of_0%_VAT',
            'value_of_acts_or_activities_paid_by_those_who_do_not_pay_the_'
            'VAT_(Exempt)',
            'tax Withheld by the taxpayer',
            'VAT for returns, discounts and rebates on purchases',
            'show_pipe', ], delimiter=',')
        fcsv_csv.writerow(
            {'type_of_third' : 'Tipo de tercero', 'type_of_operation' :\
            'Tipo de operación', 'vat' : 'RFC', 'number_id_fiscal' : \
            'Número de ID fiscal', 'foreign_name' : 'Nombre del extranjero',
            'country_of_residence' : 'País de residencia', 'nationality' : 'Nacionalidad',
            'value_of_acts_or_activities_paid_at_the_rate_of_16%' : \
            'Valor de los actos o actividades pagados a la tasa del 15% ó 16% de IVA',
            'value_of_acts_or_activities_paid_at_the_rate_of_15%' : \
            'Valor de los actos o actividades pagados a la tasa del 15% de IVA',
            'amount_of_non-creditable_VAT_paid_at_the_rate_of_16%' : \
            'Monto del IVA pagado no acreditable a la tasa del 15% ó 16%',
            'value_of_acts_or_activities_paid_at_the_rate_of_11%_VAT' : \
            'Valor de los actos o actividades pagados a la tasa del 10% u 11% de IVA',
            'value_of_acts_or_activities_paid_at_the_rate_of_10%_VAT' : \
            'Valor de los actos o actividades pagados a la tasa del 10% de IVA',
            'amount_of_non-creditable_VAT_paid_at_the_rate_of_11%' : \
            'Monto del IVA pagado no acreditable a la tasa del 10% u 11%',
            'value_of_acts_or_activities_paid_on_import_of_goods_and_services_at_the_rate_of_16%_VAT' : \
            'Valor de los actos o actividades pagados en la importación de bienes y servicios a la tasa del 15% ó 16% de IVA',
            'amount_of_non-creditable_VAT_paid_by_imports_at_the_rate_of_16%' : \
            'Monto del IVA pagado no acreditable por la importacion a la tasa del 15% ó 16%',
            'value_of_acts_or_activities_paid_on_import_of_goods_and_services_at_the_rate_of_11%_VAT' : \
            'Valor de los actos o actividades pagados en la importacion de bienes y servicios a la tasa del 10% u 11% de IVA',
            'amount_of_non-creditable_VAT_paid_by_imports_at_the_rate_of_11%' : \
            'Monto del IVA pagado no acreditable por la importacion a la tasa del 10% u 11%',
            'value_of_acts_or_activities_paid_on_import_of_goods_and_services_for_which_VAT_is_not_pay_(exempt)' : \
            'Valor de los actos o actividades pagados en la importación de bienes y servicios por los que no se paragá el IVA (Exentos)',
            'value_of_the_other_acts_or_activities_paid_at_the_rate_of_0%_VAT' : \
            'Valor de los demás actos o actividades pagados a la tasa del 0% de IVA',
            'value_of_acts_or_activities_paid_by_those_who_do_not_pay_the_VAT_(Exempt)' : \
            'Valor de los actos o actividades pagados por los que no se pagará el IVA (Exentos)',
            'tax Withheld by the taxpayer' : 'IVA Retenido por el contribuyente',
            'VAT for returns, discounts and rebates on purchases' : ' IVA correspondiente a las devoluciones, descuentos y bonificaciones'
            })
        sum_dic = {'type_of_third': '', 'value_of_acts_or_activities_paid_at_the_rate_of_16%' : 0,
            'value_of_acts_or_activities_paid_at_the_rate_of_11%_VAT' : 0,
            'value_of_the_other_acts_or_activities_paid_at_the_rate_of_0%_VAT' : 0,
            'value_of_acts_or_activities_paid_by_those_who_do_not_pay_the_VAT_(Exempt)' : 0,
            'tax Withheld by the taxpayer' : 0}
        for diot in dic_move_line:
            values_diot = dic_move_line.get(diot, False)
            fcsv.writerow(
                {'type_of_third': values_diot[0],
               'type_of_operation': values_diot[1],
               'vat': values_diot[2],
               'number_id_fiscal': values_diot[3],
               'foreign_name': values_diot[4],
               'country_of_residence': values_diot[5],
               'nationality': values_diot[6],
               'value_of_acts_or_activities_paid_at_the_rate_of_16%': int(
               round((values_diot[7]), 0)),
               'value_of_acts_or_activities_paid_at_the_rate_of_11%_VAT': int(
               round((values_diot[8]), 0)),
               'value_of_the_other_acts_or_activities_paid_at_the_rate_of'
               '_0%_VAT': int(round((values_diot[9]), 0)),
               'value_of_acts_or_activities_paid_by_those_who_do_not_pay_the'
               '_VAT_(Exempt)': int(round((values_diot[10]), 0)),
               'tax Withheld by the taxpayer': int(round((values_diot[11]), 0)),
               })
            sum_dic.update({'value_of_acts_or_activities_paid_at_the_rate_of_16%' : sum_dic['value_of_acts_or_activities_paid_at_the_rate_of_16%'] + int(round((values_diot[7]), 0)),
                'value_of_acts_or_activities_paid_at_the_rate_of_11%_VAT' : sum_dic['value_of_acts_or_activities_paid_at_the_rate_of_11%_VAT'] + int(round((values_diot[8]), 0)),
                'value_of_the_other_acts_or_activities_paid_at_the_rate_of_0%_VAT' : sum_dic['value_of_the_other_acts_or_activities_paid_at_the_rate_of_0%_VAT'] + int(round((values_diot[9]), 0)),
                'value_of_acts_or_activities_paid_by_those_who_do_not_pay_the_VAT_(Exempt)' : sum_dic['value_of_acts_or_activities_paid_by_those_who_do_not_pay_the_VAT_(Exempt)'] + int(round((values_diot[10]), 0)),
                'tax Withheld by the taxpayer' : sum_dic['tax Withheld by the taxpayer'] + int(round((values_diot[11]), 0)),
                'type_of_third': 'Total'})
            fcsv_csv.writerow(
                {'type_of_third': values_diot[0],
               'type_of_operation': values_diot[1],
               'vat': values_diot[2],
               'number_id_fiscal': values_diot[3],
               'foreign_name': values_diot[4],
               'country_of_residence': values_diot[5],
               'nationality': values_diot[6],
               'value_of_acts_or_activities_paid_at_the_rate_of_16%': int(
               round((values_diot[7]), 0)),
               'value_of_acts_or_activities_paid_at_the_rate_of_11%_VAT': int(
               round((values_diot[8]), 0)),
               'value_of_the_other_acts_or_activities_paid_at_the_rate_of'
               '_0%_VAT': int(round((values_diot[9]), 0)),
               'value_of_acts_or_activities_paid_by_those_who_do_not_pay_the'
               '_VAT_(Exempt)': int(round((values_diot[10]), 0)),
               'tax Withheld by the taxpayer': int(round((values_diot[11]), 0)),
               })
        fcsv_csv.writerow(sum_dic)
        f_write.close()
        f_write_csv.close()
        f_read = file(fname, "rb")
        fdata = f_read.read()
        out = base64.encodestring(fdata)
        name = "%s-%s-%s.txt" % ("OPENERP-DIOT", this.company_id.name,
                                     strftime('%Y-%m-%d'))
        f_read.close()
        f_read_csv = file(fname_csv, "rb")
        fdata_csv = f_read_csv.read()
        out_csv = base64.encodestring(fdata_csv)
        name_csv = "%s-%s-%s.csv" % ("OPENERP-DIOT", this.company_id.name,
                                     strftime('%Y-%m-%d'))
        f_read.close()
        datas = {'ids': context.get('active_ids', [])}
        res = self.read(cr, uid, ids, ['time_unit', 'measure_unit'])
        res = res and res[0] or {}
        datas['form'] = res
        if out:
            state = 'get'
        else:
            state = 'not_file'
        self.write(cr, uid, ids, {'state': state,
                                'file': out,
                                'file_csv' : out_csv,
                                'filename': name,
                                'filename_csv' : name_csv,
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
