# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
# #############Credits#########################################################
#    Coded by: Humberto Arocha <hbto@vauxoo.com>
###############################################################################
#    This program is free software: you can redistribute it and/or modify it
#    under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or (at your
#    option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################

from datetime import datetime

import logging
from openerp import api, models, fields
import openerp.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)

try:
    from pandas import DataFrame
except ImportError:
    _logger.info('aging_due_report is declared '
                 ' from addons-vauxoo '
                 ' you will need: sudo pip install pandas')


class AccountAgingWizardDocument(models.TransientModel):
    _name = 'account.aging.wizard.document'
    _rec_name = 'partner_id'
    _order = 'date_due'

    partner_id = fields.Many2one('res.partner', 'Partner')
    invoice_id = fields.Many2one('account.invoice', 'Invoice')
    aml_id = fields.Many2one('account.move.line',
                             'Journal Items',
                             help='Journal Item')
    residual = fields.Float('Residual')
    base = fields.Float('Base')
    tax = fields.Float('Tax')
    total = fields.Float('Total')
    payment = fields.Float('Payment')
    due_days = fields.Integer(string='Due Days')
    date_emission = fields.Date('Emission Date')
    date_due = fields.Date('Due Date')
    company_id = fields.Many2one('res.company', u'Company')
    currency_id = fields.Many2one('res.currency', 'Currency')
    aaw_id = fields.Many2one('account.aging.wizard',
                             'Account Aging Wizard',
                             help='Account Aging Wizard Holder')
    aawp_id = fields.Many2one('account.aging.wizard.partner',
                              'Account Aging Wizard Partner',
                              help='Account Aging Wizard Partner')


class AccountAgingWizardPartner(models.TransientModel):
    _name = 'account.aging.wizard.partner'
    _description = 'Account Aging Wizard Partner'
    _rec_name = 'partner_id'
    _order = 'name'

    @api.model
    def _get_amount_span(self, field_names, res_line, doc, spans, direction):
        len_span = len(spans) if spans else 0
        first_item = 0
        last_item = len_span - 1
        span_items = range(len_span)
        if not direction:
            span_items.reverse()
            first_item, last_item = last_item, first_item
        for item in span_items:
            span = 'span%02d' % (item + 1)
            if span not in field_names:
                continue

            lt_lim = gt_lim = True
            if not direction:
                if first_item == item:
                    gt_lim = spans[item] >= doc.due_days
                else:
                    lt_lim = spans[item + 1] < doc.due_days
                    gt_lim = spans[item] >= doc.due_days
            else:
                if last_item == item:
                    lt_lim = spans[item] < doc.due_days
                else:
                    lt_lim = spans[item] < doc.due_days
                    gt_lim = spans[item + 1] >= doc.due_days

            if lt_lim and gt_lim:
                res_line[span] += doc.residual

    partner_id = fields.Many2one('res.partner', string='Partner',
                                 required=True)
    name = fields.Char(string="Name", related='partner_id.name',
                       store=True)
    aaw_id = fields.Many2one('account.aging.wizard',
                             'Account Aging Wizard',
                             help='Account Aging Wizard Holder')
    document_ids = fields.One2many('account.aging.wizard.document',
                                   'aawp_id', 'Documents',
                                   help='Balance by Currency')
    aml_ids = fields.Many2many('account.move.line',
                               'aaw_id', 'Journal Items',
                               help='Journal Items')
    currency_id = fields.Many2one('res.currency', 'Currency',
                                  required=True)
    total = fields.Float(string='Total', digits=dp.get_precision('Account'))
    payment = fields.Float(string='Payment',
                           digits=dp.get_precision('Account'))
    residual = fields.Float(string='Residual',
                            digits=dp.get_precision('Account'))
    not_due = fields.Float(string='Not Due',
                           digits=dp.get_precision('Account'))
    span01 = fields.Float(string='span01',
                          digits=dp.get_precision('Account'))
    span02 = fields.Float(string='span02',
                          digits=dp.get_precision('Account'))
    span03 = fields.Float(string='span03',
                          digits=dp.get_precision('Account'))
    span04 = fields.Float(string='span04',
                          digits=dp.get_precision('Account'))
    span05 = fields.Float(string='span05',
                          digits=dp.get_precision('Account'))
    aawc_id = fields.Many2one('account.aging.wizard.currency',
                              'Account Aging Wizard Currency',
                              help='Account Aging Wizard Currency Holder')


class AccountAgingWizardCurrency(models.TransientModel):
    _name = 'account.aging.wizard.currency'
    _description = 'Account Aging Wizard Currency'
    _rec_name = 'currency_id'

    currency_id = fields.Many2one('res.currency', 'Currency',
                                  required=True)
    aaw_id = fields.Many2one('account.aging.wizard',
                             'Account Aging Wizard',
                             help='Account Aging Wizard Holder')
    partner_ids = fields.One2many('account.aging.wizard.partner',
                                  'aawc_id', 'Partner by Currency',
                                  help='Partner by Currency')
    residual = fields.Float(string='Residual',
                            digits=dp.get_precision('Account'))
    not_due = fields.Float(string='Not Due',
                           digits=dp.get_precision('Account'))
    span01 = fields.Float(string='span01',
                          digits=dp.get_precision('Account'))
    span02 = fields.Float(string='span02',
                          digits=dp.get_precision('Account'))
    span03 = fields.Float(string='span03',
                          digits=dp.get_precision('Account'))
    span04 = fields.Float(string='span04',
                          digits=dp.get_precision('Account'))
    span05 = fields.Float(string='span05',
                          digits=dp.get_precision('Account'))


class AccountAgingPartnerWizard(models.TransientModel):
    _name = 'account.aging.wizard'
    _description = 'Price List'
    _rec_name = 'result_selection'

    report_format = fields.Selection(
        [
            ('pdf', 'PDF'),
            # TODO: enable print on controller to HTML
            # ('html', 'HTML'),
            ('xls', 'Spreadsheet')
        ], 'Report Format',
        required=True, default='pdf')
    result_selection = fields.Selection(
        [
            ('supplier', 'Payable'),
            ('customer', 'Receivable')
        ], "Target",
        required=True, default='customer')
    type = fields.Selection(
        [
            ('aging', 'Aging Report'),
            ('detail', 'Detailed Report'),
            ('aging_detail', 'Aging Detailed Report')
        ],  # ('formal', 'Formal Report')],
        "Type",
        required=True, default='aging')
    currency_ids = fields.One2many(
        'account.aging.wizard.currency',
        'aaw_id', 'Balance by Currency',
        help='Balance by Currency')
    document_ids = fields.One2many(
        'account.aging.wizard.document',
        'aaw_id', 'Document',
        help='Document')
    partner_ids = fields.One2many(
        'account.aging.wizard.partner',
        'aaw_id', 'Partners',
        help='Partners')
    company_id = fields.Many2one(
        'res.company', 'Company', required=True,
        default=lambda self: self.env['res.company']._company_default_get(
            'account.aging.wizard'))
    period_length = fields.Integer(
        'Period Length (days)', required=True, default='30')
    user_id = fields.Many2one(
        'res.users', 'User', default=lambda self: self.env.user)
    direction = fields.Selection(
        [
            ('future', 'Future'),
            ('past', 'Past')
        ], "Direction",
        required=True, default='past')

    @api.multi
    def _get_lines_by_partner_without_invoice(self, rp_ids):
        wzd_brw = self[0]
        aml_obj = self.env['account.move.line']
        company_id = wzd_brw.company_id.id

        moves_invoice_ids = [aawd_brw.invoice_id.move_id.id
                             for aawp_brw in wzd_brw.partner_ids
                             for aawd_brw in aawp_brw.document_ids
                             if aawd_brw.invoice_id]

        items_invoice_ids = [
            aml_brw.id for aawp_brw in wzd_brw.partner_ids
            for aawd_brw in aawp_brw.document_ids
            for aml_brw in aawd_brw.invoice_id.payment_ids
            if aawd_brw.invoice_id]

        args = [
            ('reconcile_id', '=', False),
            ('move_id', 'not in', moves_invoice_ids),
            ('id', 'not in', items_invoice_ids),
            ('company_id', '=', company_id),
            ('partner_id', 'child_of', rp_ids)
        ]

        sel = wzd_brw.result_selection
        if sel == 'customer':
            args += [('account_id.type', '=', 'receivable')]
        elif sel == 'supplier':
            args += [('account_id.type', '=', 'payable')]
        aml_ids = aml_obj.search(args)
        res = []

        # From here on create a new method that consumes the aml_ids
        # This method make the groupings and return the results ready to be
        # used in the original place where the method was called
        if not aml_ids:
            return []
        aml_rd = aml_ids.read(['partner_id', 'reconcile_partial_id', 'debit',
                               'credit', 'amount_currency', 'currency_id'])
        aml_data = DataFrame(aml_rd).set_index('id')
        aml_data_grouped = aml_data.groupby(['partner_id',
                                             'reconcile_partial_id'])

        aml_data_groups = aml_data_grouped.groups

        for key, val in aml_data_groups.iteritems():
            partner_id, reconcile_id = key
            aml_lines = aml_obj.browse(val)
            if reconcile_id:
                # TODO: This process can be improve by using the approach reach
                # in commission_payment
                date_due = [amx_brw.date_maturity or amx_brw.date
                            for amx_brw in aml_lines
                            if amx_brw.journal_id.type in ('sale', 'purchase')]
                date_due = (date_due and min(date_due) or
                            min([amy_brw.date_maturity or amy_brw.date
                                 for amy_brw in aml_lines]))
                date_emission = [amz_brw.date
                                 for amz_brw in aml_lines
                                 if amz_brw.journal_id.type in (
                                     'sale', 'purchase')]
                date_emission = (date_emission and min(date_emission) or
                                 min([amw_brw.date
                                      for amw_brw in aml_lines]))
                aml_id = [amv_brw.id
                          for amv_brw in aml_lines
                          if (amv_brw.journal_id.type in (
                              'sale', 'purchase') and
                              amv_brw.date == date_emission)]
                aml_id = (aml_id or [
                    amu_brw.id for amu_brw in aml_lines
                    if amu_brw.date == date_emission])

                doc = {
                    'partner_id': partner_id[0],
                    'aml_id': aml_id[0],
                    # 'wh_vat': wh_vat,
                    # 'wh_islr': wh_islr,
                    # 'wh_muni': wh_muni,
                    # 'wh_src': wh_src,
                    # 'debit_note': debit_note,
                    # 'credit_note': credit_note,
                    # 'refund_brws': refund_brws,
                    'payment': 0.0,
                    # 'payment_left': payment_left,
                    'residual': 0.0,
                    'currency_id': False,
                    'total': 0.0,
                    'base': 0.0,
                    'date_emission': date_emission,
                    'date_due': date_due}
            for aml_brw in aml_lines:
                if aml_brw.currency_id:
                    currency_id = aml_brw.currency_id.id
                    total = (sel == 'customer' and
                             aml_brw.amount_currency > 0 and
                             aml_brw.amount_currency or
                             sel == 'supplier' and
                             aml_brw.amount_currency < 0 and
                             (-1) * aml_brw.amount_currency or 0.0)
                    payment = (sel == 'customer' and
                               aml_brw.amount_currency < 0 and
                               (-1) * aml_brw.amount_currency or
                               sel == 'supplier' and
                               aml_brw.amount_currency > 0 and
                               aml_brw.amount_currency or 0.0)
                else:
                    currency_id = aml_brw.company_id.currency_id.id
                    total = (sel == 'customer' and aml_brw.debit or
                             sel == 'supplier' and aml_brw.credit or 0.0)
                    payment = (sel == 'customer' and aml_brw.credit or
                               sel == 'supplier' and aml_brw.debit or 0.0)
                if not reconcile_id:
                    date_due = aml_brw.date_maturity or aml_brw.date
                    res.append({
                        'partner_id': aml_brw.partner_id.id,
                        'aml_id': aml_brw.id,
                        # 'wh_vat': wh_vat,
                        # 'wh_islr': wh_islr,
                        # 'wh_muni': wh_muni,
                        # 'wh_src': wh_src,
                        # 'debit_note': debit_note,
                        # 'credit_note': credit_note,
                        # 'refund_brws': refund_brws,
                        'payment': -payment,
                        # 'payment_left': payment_left,
                        'residual': (total - payment),
                        'currency_id': currency_id,
                        'total': total,
                        'base': total,
                        'date_emission': aml_brw.date,
                        'date_due': date_due})
                else:
                    # TODO: When currency_id is not None then convert values or
                    # use other values like amount_currency
                    # Problem here is that in a single reconciliation there
                    # could be more than one currency
                    doc['currency_id'] = currency_id
                    doc['payment'] -= payment
                    doc['total'] += total
                    doc['base'] += total
                    doc['residual'] += (total - payment)
            if reconcile_id:
                res.append(doc)
        return res

    @api.multi
    def _get_aml(self, aml_ids, inv_type='out_invoice', currency_id=None):
        res = 0.0
        if not aml_ids:
            return res
        sign = 1 if inv_type == 'out_invoice' else -1
        if currency_id:
            amount = aml_ids.read_group(
                [('id', 'in', aml_ids.ids), ('amount_currency', '!=', 0)],
                ['amount_currency'], [])
            amount = amount[0] if amount else {}
            res = amount.get('amount_currency', 0)
        else:
            amount = aml_ids.read_group(
                [('id', 'in', aml_ids.ids)], ['debit', 'credit'], [])
            amount = amount[0] if amount else {}
            res = amount.get('debit', 0) - amount.get('credit', 0)
        return res * sign

    @api.multi
    def _get_invoice_by_partner(self, partner_ids,
                                inv_type='out_invoice'):
        """return a dictionary of dictionaries.
            { partner_id: { values and invoice list } }
        """
        res = []
        inv_obj = self.env['account.invoice']
        rp_obj = self.env['res.partner']
        aml_obj = self.env['account.move.line']
        # Filtering Partners by Unique Accounting Partners
        fap_fnc = rp_obj._find_accounting_partner
        invoices = inv_obj.search(
            [('partner_id', 'child_of', partner_ids),
             ('type', '=', inv_type),
             ('residual', '!=', 0),
             ('state', 'not in', ('cancel', 'draft'))])
        if not invoices:
            return res

        for invoice in invoices:
            currency_id = (invoice.currency_id.id !=
                           invoice.company_id.currency_id.id and
                           invoice.currency_id.id)
            payment = self._get_aml(
                invoice.payment_ids, inv_type, currency_id)
            residual = invoice.amount_total + payment

            if not residual:
                continue

            date_maturity = aml_obj.search_read(
                [('account_id.type', 'in', ['receivable', 'payable']),
                 ('date_maturity', '!=', None),
                 ('move_id', '=', invoice.move_id.id)], ['date_maturity'],
                limit=1, order='date_maturity ASC')
            date_due = ((date_maturity[0]['date_maturity']
                        if date_maturity else invoice.date_due) or
                        invoice.date_invoice)

            res.append({
                'invoice_id': invoice.id,
                'currency_id': invoice.currency_id.id,
                'partner_id': fap_fnc(invoice.partner_id).id,
                'payment': payment,
                'residual': residual,
                'total': invoice.amount_total,
                'tax': invoice.amount_tax,
                'base': invoice.amount_untaxed,
                'date_due': date_due,
                'date_emission': invoice.date_invoice,
            })

        return res

    @api.multi
    def compute_lines(self, partner_ids):
        rp_obj = self.env['res.partner']

        # Filtering Partners by Unique Accounting Partners
        fap_fnc = rp_obj._find_accounting_partner
        rp_brws = rp_obj.browse(partner_ids)
        partner_ids = [fap_fnc(rp_brw).id for rp_brw in rp_brws]
        partner_ids = list(set(partner_ids))

        aawc_obj = self.env['account.aging.wizard.currency']
        aawp_obj = self.env['account.aging.wizard.partner']
        aawd_obj = self.env['account.aging.wizard.document']

        wzd_brw = self[0]
        if wzd_brw.result_selection == 'customer':
            inv_type = 'out_invoice'
        elif wzd_brw.result_selection == 'supplier':
            inv_type = 'in_invoice'

        wzd_brw.document_ids.unlink()
        wzd_brw.partner_ids.unlink()
        wzd_brw.currency_ids.unlink()
        aawp_ids = {}
        aawc_ids = {}

        today = datetime.now()

        for each in self._get_invoice_by_partner(
                partner_ids, inv_type=inv_type):
            partner_id = each['partner_id']
            currency_id = each['currency_id']
            key_pair = (partner_id, currency_id)
            if not aawc_ids.get(currency_id, False):
                aawc_id = aawc_obj.create({
                    'aaw_id': wzd_brw.id,
                    'currency_id': currency_id,
                })
                aawc_ids[currency_id] = aawc_id.id
            if not aawp_ids.get(key_pair, False):
                aawp_id = aawp_obj.create({
                    'aaw_id': wzd_brw.id,
                    'partner_id': partner_id,
                    'currency_id': currency_id,
                    'aawc_id': aawc_ids[currency_id],
                })
                aawp_ids[partner_id, currency_id] = aawp_id.id
            each['aawp_id'] = aawp_ids[partner_id, currency_id]
            each['aaw_id'] = wzd_brw.id
            each['due_days'] = self._get_due_days(today, each)
            aawd_obj.create(each)

        for line in self._get_lines_by_partner_without_invoice(partner_ids):
            partner_id = line['partner_id']
            currency_id = line['currency_id']
            key_pair = (partner_id, currency_id)
            if not aawc_ids.get(currency_id, False):
                aawc_id = aawc_obj.create({
                    'aaw_id': wzd_brw.id,
                    'currency_id': currency_id,
                })
                aawc_ids[currency_id] = aawc_id.id
            if not aawp_ids.get(key_pair, False):
                aawp_id = aawp_obj.create({
                    'aaw_id': wzd_brw.id,
                    'partner_id': partner_id,
                    'currency_id': currency_id,
                    'aawc_id': aawc_ids[currency_id],
                })
                aawp_ids[partner_id, currency_id] = aawp_id.id
            line['aawp_id'] = aawp_ids[partner_id, currency_id]
            line['aaw_id'] = wzd_brw.id
            line['due_days'] = self._get_due_days(today, line)
            aawd_obj.create(line)

        # Only to trigger _get_amount
        wzd_brw._get_amount()
        return True

    def _get_amount(self):
        field_sum = ['residual', 'payment', 'total', 'not_due']
        field_spans = ['span01', 'span02', 'span03', 'span04', 'span05']
        field_names = field_spans + field_sum
        wzd_cur_fields = field_spans + ['not_due', 'residual']
        direction = self.direction == 'past'
        spans = [
            self.period_length * x * (direction and 1 or -1)
            for x in range(5)]

        for wzd_cur in self.currency_ids:
            for fn in wzd_cur_fields:
                wzd_cur._cache[fn] = 0.0
            for part in wzd_cur.partner_ids:
                res = {}.fromkeys(field_names, 0.0)
                docs = part.document_ids
                field_sum_res = docs.read_group(
                    [('id', 'in', docs.ids)], field_sum, [])

                field_sum_res = field_sum_res[0] if field_sum_res else {}
                res.update(dict((field, field_sum_res.get(field, 0))
                                for field in field_sum))
                not_due_docs = (
                    docs.filtered(lambda r: r.due_days <= 0) if direction else
                    docs.filtered(lambda r: r.due_days > 0))
                not_due_sum = docs.read_group(
                    [('id', 'in', not_due_docs.ids)], ['residual'], [])
                not_due_sum = not_due_sum[0] if not_due_sum else {}

                res['not_due'] = not_due_sum.get('residual') or 0

                for due_record in docs - not_due_docs:
                    part._get_amount_span(
                        field_spans, res, due_record, spans, direction)

                part.update(res)

                for fn in wzd_cur_fields:
                   wzd_cur._cache[fn] += res.get(fn) or 0
            wzd_cur.write(wzd_cur._convert_to_write(wzd_cur._cache))
        return

    def _get_due_days(self, today, record):
        date_due = datetime.strptime(record['date_due'], '%Y-%m-%d')
        return (today - date_due).days

    @api.multi
    def print_report(self):
        """To get the date and print the report
        @return : return report
        """
        ctx = self._context.copy()
        self.compute_lines(self.env.context.get('active_ids', []))
        datas = {'active_ids': self.env.context.get('active_ids', [])}
        ctx['active_model'] = 'account.aging.wizard'
        wzd_brw = self[0]
        ctx['xls_report'] = wzd_brw.report_format == 'xls'
        name = 'aging_due_report.aging_due_report_qweb'
        if wzd_brw.type == 'aging':
            name = 'aging_due_report.aging_due_report_qweb'
        if wzd_brw.type == 'aging_detail':
            name = 'aging_due_report.aging_detail_due_report_qweb'
        if wzd_brw.type == 'detail':
            name = 'aging_due_report.detail_due_report_qweb'
        if wzd_brw.result_selection == 'customer':
            if wzd_brw.type == 'formal':
                name = 'aging_due_report.formal_due_report_qweb'
        elif wzd_brw.result_selection == 'supplier':
            if wzd_brw.type == 'formal':
                name = 'aging_due_report.supplier_formal_due_report_qweb'
        return self.env['report'].with_context(ctx).get_action(self,
                                                               name,
                                                               datas)
