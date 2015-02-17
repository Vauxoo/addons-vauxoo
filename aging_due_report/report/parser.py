#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: Humberto Arocha <hbto@vauxoo.com>
#    Planified by: Rafael Silva <rsilvam@vauxoo.com>
#    Audited by: Nhomar Hernandez <nhomar@vauxoo.com>
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##########################################################################


import time
from openerp.report import report_sxw
import mx.DateTime
from openerp.osv import osv
from datetime import datetime


class aging_parser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(aging_parser, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'int': int,
            'get_invoice_by_partner': self._get_invoice_by_partner,
            'get_total_by_comercial': self._get_total_by_comercial,
            'get_aged_lines': self._get_aged_lines,
            'get_invoice_by_currency': self._get_invoice_by_currency,
            'get_invoice_by_partner_group': self._get_invoice_by_partner_group,
            'get_invoice_by_currency_group':
            self._get_invoice_by_currency_group,
            'datetime': datetime,
        })

    def _get_aml(self, ids, inv_type='out_invoice', currency_id=None):
        aml_obj = self.pool.get('account.move.line')
        res = 0.0
        sign = 1 if inv_type == 'out_invoice' else -1
        if not ids:
            return res
        if currency_id:
            aml_gen = (
                aml_brw.amount_currency * sign
                for aml_brw in aml_obj.browse(self.cr, self.uid, ids))
            for i in aml_gen:
                res += i
        else:
            aml_gen = (aml_brw.debit and (aml_brw.debit * sign) or
                       aml_brw.credit * (-1 * sign) for aml_brw in
                       aml_obj.browse(self.cr, self.uid, ids))
            for i in aml_gen:
                res += i
        return res

    def _get_total_by_comercial(self, rp_brws, inv_type='out_invoice'):
        """
        return a list of dictionarios with the total and without vendor
        amounts, one item for every currency find.
        """
        ixp_gen = self._get_invoice_by_partner(rp_brws, inv_type)
        usr_dict = {}
        res = dict()

        for ixp in ixp_gen:
            usr_id = ixp['rp_brw'].user_id and ixp[
                'rp_brw'].user_id.id or False

            if usr_dict.get((usr_id, ixp['cur_brw'].id), False):
                usr_dict[(usr_id, ixp['cur_brw'].id)]['total'] += \
                    ixp['due_total']
            else:
                usr_dict[(usr_id, ixp['cur_brw'].id)] = {
                    'cur_brw': ixp['cur_brw'],
                    'usr_brw': ixp['rp_brw'].user_id,
                    'total': ixp['due_total']
                }

            if res.get(ixp['cur_brw'].id, False):
                res[ixp['cur_brw'].id]['total'] += ixp['due_total']
            else:
                res[ixp['cur_brw'].id] = dict()
                res[ixp['cur_brw'].id]['currency'] = ixp['cur_brw'].name
                res[ixp['cur_brw'].id]['total'] = ixp['due_total']
                res[ixp['cur_brw'].id]['vendor'] = []

        for user_cur in usr_dict:
            if res.get(user_cur[1], False):
                res[user_cur[1]]['vendor'] += [usr_dict[user_cur]['total']]
            else:
                res[user_cur[1]]['vendor'] = [usr_dict[user_cur]['total']]
                # {'total': total, 'vendor': (usr_dict[i] for i in usr_dict)},

        if not res:
            return []
        return res.values()

    def _get_invoice_by_partner(self, rp_brws, inv_type='out_invoice'):
        """
        return a dictionary of dictionaries.
            { partner_id: { values and invoice list } }
        """
        res = {}
        rp_obj = self.pool.get('res.partner')
        inv_obj = self.pool.get('account.invoice')
        cur_obj = self.pool.get('res.currency')
        for rp_brw in rp_brws:
            inv_ids = inv_obj.search(
                self.cr, self.uid, [('partner_id', '=', rp_brw.id),
                                    ('type', '=', inv_type),
                                    ('residual', '!=', 0),
                                    ('state', 'not in',
                                    ('cancel', 'draft'))])
            if not inv_ids:
                continue

            inv_by_currency = self._get_invoice_by_currency(inv_ids)
            res[rp_brw.id] = {}.fromkeys(inv_by_currency.keys())

            for currency_id in res[rp_brw.id].keys():
                res[rp_brw.id][currency_id] = {
                    'rp_brw': rp_brw,
                    'cur_brw': cur_obj.browse(self.cr, self.uid, currency_id),
                    'inv_ids': [],
                    'inv_total': 0.0,
                    'wh_vat': 0.0,
                    'wh_islr': 0.0,
                    'wh_muni': 0.0,
                    'credit_note': 0.0,
                    'pay_left_total': 0.0,
                    'pay_total': 0.0,
                    'due_total': 0.0,
                }

                for inv_brw in inv_obj.browse(
                    self.cr, self.uid,
                        inv_by_currency[currency_id]):

                    currency_data = dict(
                        invoice=inv_brw.currency_id.id,
                        company=inv_brw.company_id.currency_id.id)
                    currency_data.update(
                        transaction=None if
                        len(set(currency_data.values())) == 1
                        else currency_data['invoice'])

                    pay_ids = [aml.id for aml in inv_brw.payment_ids]
                    # ~ VAT
                    pay_vat_ids = []
                    # ~ ISLR
                    pay_islr_ids = []
                    # ~  MUNI
                    pay_muni_ids = []
                    # ~  TODO: SRC

                    # ~ N/C
                    # ~ refund_ids = inv_obj.search(self.cr,self.uid,
                    # [('parent_id','=',inv_brw.id),('type','=','out_refund'),
                    # ('state','not in',('draft','cancel')),
                    # ('move_id','!=',False)])
                    # ~ refund_ids = inv_obj.search(self.cr,self.uid,
                    # [('parent_id','=',inv_brw.id),('type','=','out_refund'),
                    # ('state','not in',('draft','cancel')),
                    # ('move_id','!=',False)])
                    refund_brws = []
                    # ~ refund_brws = refund_ids and inv_obj.browse(
                    # self.cr,self.uid,refund_ids) or []
                    # ~ aml_gen = (refund_brw.move_id.line_id for
                    # refund_brw in refund_brws)
                    pay_refund_ids = []
                    # ~ for aml_brws in aml_gen:
                    # ~ pay_refund_ids += [aml.id for aml in aml_brws
                    # if aml.account_id.id == inv_brw.account_id.id]

                    # ~  TODO: N/D
                    # ~  ACUMULACION DE LOS NOPAGOS, OBTENCION DEL PAGO
                    pay_left_ids = list(set(pay_ids).difference(
                        pay_vat_ids +
                        pay_islr_ids +
                        pay_muni_ids +
                        pay_refund_ids))
                    wh_vat = self._get_aml(
                        pay_vat_ids, inv_type, currency_data['transaction'])
                    wh_islr = self._get_aml(
                        pay_islr_ids, inv_type, currency_data['transaction'])
                    wh_muni = self._get_aml(
                        pay_muni_ids, inv_type, currency_data['transaction'])
                    wh_src = self._get_aml(
                        [], inv_type, currency_data['transaction'])
                    debit_note = self._get_aml(
                        [], inv_type, currency_data['transaction'])
                    credit_note = self._get_aml(
                        pay_refund_ids, inv_type, currency_data['transaction'])
                    payment_left = self._get_aml(
                        pay_left_ids, inv_type, currency_data['transaction'])
                    payment = wh_vat + wh_islr + wh_muni + \
                        wh_src + debit_note + credit_note + payment_left
                    residual = inv_brw.amount_total + payment
                    date_due = mx.DateTime.strptime(
                        inv_brw.date_due or inv_brw.date_invoice, '%Y-%m-%d')
                    today = mx.DateTime.now()
                    due_days = (today - date_due).day

                    # ~ TODO: Si se incluye un reporte de revisiones
                    # ~ no se eliminara la factura
                    # ~ si la factura no tiene saldo entonces
                    # ~ no incluirla en el reporte
                    if not residual:
                        continue

                    res[rp_brw.id][currency_id]['inv_ids'].append({
                        'inv_brw': inv_brw,
                        'wh_vat': wh_vat,
                        'wh_islr': wh_islr,
                        'wh_muni': wh_muni,
                        'wh_src': wh_src,
                        'debit_note': debit_note,
                        'credit_note': credit_note,
                        'refund_brws': refund_brws,
                        'payment': payment,
                        'payment_left': payment_left,
                        'residual': residual,
                        'due_days': due_days
                    })
                    res[rp_brw.id][currency_id]['inv_total'] += \
                        inv_brw.amount_total
                    res[rp_brw.id][currency_id]['wh_vat'] += wh_vat
                    res[rp_brw.id][currency_id]['wh_islr'] += wh_islr
                    res[rp_brw.id][currency_id]['wh_muni'] += wh_muni
                    res[rp_brw.id][currency_id]['credit_note'] += credit_note
                    res[rp_brw.id][currency_id]['pay_left_total'] += \
                        payment_left
                    res[rp_brw.id][currency_id]['pay_total'] += payment
                    res[rp_brw.id][currency_id]['due_total'] += residual

            # ~ TODO: Report donde no se elimine esta clave del diccionario
            # ~ y se use para revisiones internas
            # ~ Si no tiene saldo, sacarlo del reporte
            not res[rp_brw.id][currency_id]['due_total'] and res.pop(rp_brw.id)

        # ~ ordenando los registros en orden alfabetico
        # ~ si llegaran a existir
        res2 = []
        if res.keys():
            rp_ids = rp_obj.search(self.cr, self.uid, [(
                'id', 'in', res.keys())], order='name asc')
            for rp_id in rp_ids:
                for currency_id in res[rp_id].keys():
                    res2.append(res[rp_id][currency_id])
        return res2

    def _get_invoice_by_partner_group(self, rp_brws, inv_type='out_invoice'):
        """
        process the invoice data generate and groupebd in list by partner.
        """
        res = self._get_invoice_by_partner(rp_brws, inv_type)
        res2 = dict()
        for item in res:
            if res2.get(item['rp_brw'].id, False):
                res2[item['rp_brw'].id] += [item]
            else:
                res2[item['rp_brw'].id] = [item]

        res3 = res2.values()
        return res3

    def _get_invoice_by_currency_group(self, rp_brws, inv_type='out_invoice'):
        """
        process the invoice data generate and groupebd in list by currency.
        """
        res = self._get_invoice_by_partner(rp_brws, inv_type)
        res2 = dict()
        for item in res:
            if res2.get(item['cur_brw'].id, False):
                res2[item['cur_brw'].id] += [item]
            else:
                res2[item['cur_brw'].id] = [item]
        return res2.values()

    def _get_invoice_by_currency(self, inv_ids):
        """
        a dictioary with subgroups of the given invoices grouped by currency.
        """
        res = {}
        inv_obj = self.pool.get('account.invoice')
        for inv_brw in inv_obj.browse(self.cr, self.uid, inv_ids):
            if res.get(inv_brw.currency_id.id, False):
                res[inv_brw.currency_id.id] += [inv_brw.id]
            else:
                res[inv_brw.currency_id.id] = [inv_brw.id]
        return res

    def _get_aged_lines(self, rp_brws, span=30,
                        date_from=time.strftime('%Y-%m-%d'),
                        inv_type='out_invoice'):
        """
        @return
        """
        # span = 30
        # spans = [0, 30, 60, 90, 120]
        # span = 90
        # spans = [0, 90, 180, 270, 360]
        spans = [span * x for x in range(5)]

        if not rp_brws:
            return []

        ixp_gen = self._get_invoice_by_currency_group(rp_brws, inv_type)

        if not ixp_gen:
            return []

        '''
        [
            {
            'rp_brw':rp_brw,
            'inv_ids':[{
                    'residual':residual,
                    'due_days':due_days
                }],
            'due_total':due_total,
            }
        ]
        '''

        '''
            [{
                'id'        : ixp['rp_brw'].id,
                'rp_brw'    : ixp['rp_brw'],
                'not_due'   : 0.00,
                '1to30'     : 0.00,
                '31to60'    : 0.00,
                '61to90'    : 0.00,
                '91to120'   : 0.00,
                '120+'      : 0.00,
            }]
        '''

        res_total_by_currency = dict()
        res_total = {
            'type': 'total',
            'not_due': 0.00,
            '1to30': 0.00,
            '31to60': 0.00,
            '61to90': 0.00,
            '91to120': 0.00,
            '120+': 0.00,
            'total': 0.00,
        }

        result = []
        for currency_group in ixp_gen:
            for ixp in currency_group:
                res = {
                    'type': 'partner',
                    'rp_brw': ixp['rp_brw'],
                    'cur_brw': ixp['cur_brw'],
                    'not_due': 0.00,
                    '1to30': 0.00,
                    '31to60': 0.00,
                    '61to90': 0.00,
                    '91to120': 0.00,
                    '120+': 0.00,
                    'total': 0.00,
                }

                for inv in ixp['inv_ids']:
                    currency_id = ixp['cur_brw'].id
                    if not res_total_by_currency.get(currency_id, False):
                        res_total_by_currency[currency_id] = res_total.copy()
                        res_total_by_currency[currency_id]['cur_brw'] = \
                            ixp['cur_brw']

                    res['total'] += inv['residual']
                    res_total_by_currency[currency_id]['total'] += \
                        inv['residual']

                    if inv['due_days'] <= 0:
                        res['not_due'] += inv['residual']
                        res_total_by_currency[currency_id]['not_due'] += \
                            inv['residual']
                    elif inv['due_days'] > 0 and inv['due_days'] <= spans[1]:
                        res['1to30'] += inv['residual']
                        res_total_by_currency[currency_id]['1to30'] += \
                            inv['residual']
                    elif inv['due_days'] > spans[1] and inv['due_days'] <= \
                            spans[2]:
                        res['31to60'] += inv['residual']
                        res_total_by_currency[currency_id]['31to60'] += \
                            inv['residual']
                    elif inv['due_days'] > spans[2] and inv['due_days'] <= \
                            spans[3]:
                        res['61to90'] += inv['residual']
                        res_total_by_currency[currency_id]['61to90'] += \
                            inv['residual']
                    elif inv['due_days'] > spans[3] and inv['due_days'] <= \
                            spans[4]:
                        res['91to120'] += inv['residual']
                        res_total_by_currency[currency_id]['91to120'] += \
                            inv['residual']
                    else:
                        res['120+'] += inv['residual']
                        res_total_by_currency[currency_id]['120+'] += \
                            inv['residual']
                result.append(res)

        result.extend(res_total_by_currency.values())

        # calculate the provisions totals over the totals rows
        res_prov = dict()
        total_col_sum = ['not_due', '1to30', '31to60',
                         '61to90', '91to120', '120+']
        for (key, value) in res_total_by_currency.iteritems():
            res_prov[key] = value.copy()

        for (currency_id, value) in res_prov.iteritems():
            res_prov[currency_id]['type'] = 'provision'
            res_prov[currency_id]['31to60'] *= 0.25
            res_prov[currency_id]['61to90'] *= 0.5
            res_prov[currency_id]['91to120'] *= 0.75
            res_prov[currency_id]['total'] = sum([
                res_prov[currency_id][col] for col in total_col_sum])
        result.extend(res_prov.values())

        result2 = dict()
        for item in result:
            currency_id = item.get('cur_brw', False)
            currency_id = currency_id and currency_id.id
            if result2.get(currency_id, False):
                result2[currency_id] += [item]
            else:
                result2[currency_id] = [item]

        return result2.values()


class aging_parser_qweb_pdf_report(osv.AbstractModel):
    _name = 'report.aging_due_report.aging_due_report_qweb'
    _inherit = 'report.abstract_report'
    _template = 'aging_due_report.aging_due_report_qweb'
    _wrapped_report_class = aging_parser


class formal_parser_qweb_pdf_report(osv.AbstractModel):
    _name = 'report.aging_due_report.formal_due_report_qweb'
    _inherit = 'report.abstract_report'
    _template = 'aging_due_report.formal_due_report_qweb'
    _wrapped_report_class = aging_parser


class detail_parser_qweb_pdf_report(osv.AbstractModel):
    _name = 'report.aging_due_report.detail_due_report_qweb'
    _inherit = 'report.abstract_report'
    _template = 'aging_due_report.detail_due_report_qweb'
    _wrapped_report_class = aging_parser


class supplier_aging_parser_qweb_pdf_report(osv.AbstractModel):
    _name = 'report.aging_due_report.supplier_aging_due_report_qweb'
    _inherit = 'report.abstract_report'
    _template = 'aging_due_report.supplier_aging_due_report_qweb'
    _wrapped_report_class = aging_parser


class supplier_detail_parser_qweb_pdf_report(osv.AbstractModel):
    _name = 'report.aging_due_report.supplier_detail_due_report_qweb'
    _inherit = 'report.abstract_report'
    _template = 'aging_due_report.supplier_detail_due_report_qweb'
    _wrapped_report_class = aging_parser


class supplier_formal_parser_qweb_pdf_report(osv.AbstractModel):
    _name = 'report.aging_due_report.supplier_formal_due_report_qweb'
    _inherit = 'report.abstract_report'
    _template = 'aging_due_report.supplier_formal_due_report_qweb'
    _wrapped_report_class = aging_parser

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
