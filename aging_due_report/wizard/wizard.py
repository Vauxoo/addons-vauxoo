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

from openerp.tools.translate import _
from openerp.osv import fields, osv
from datetime import datetime

import logging
_logger = logging.getLogger(__name__)


class AccountAgingWizardDocument(osv.TransientModel):
    _name = 'account.aging.wizard.document'
    _rec_name = 'partner_id'
    _order = 'due_days'

    def _get_due_days(self, cr, uid, ids, field_names, arg, context=None):
        context = dict(context or {})
        res = {}.fromkeys(ids, False)
        today = datetime.now()
        for line in self.browse(cr, uid, ids, context=context):
            if line.date_due:
                date_due = datetime.strptime(line.date_due, '%Y-%m-%d')
                res[line.id] = (today - date_due).days
        return res

    _columns = {
        'partner_id': fields.many2one('res.partner', u'Partner'),
        'invoice_id': fields.many2one('account.invoice', 'Invoice'),
        'aml_id': fields.many2one(
            'account.move.line',
            'Journal Items',
            help='Journal Item'),
        'residual': fields.float('Residual'),
        'base': fields.float('Base'),
        'tax': fields.float('Tax'),
        'total': fields.float('Total'),
        'payment': fields.float('Payment'),
        'due_days': fields.function(
            _get_due_days,
            string='Due Days',
            store={
                _name: (lambda self, cr, uid, ids, cx: ids, [], 15),
            },
            type='integer'),
        'date_emission': fields.date('Emission Date'),
        'date_due': fields.date('Due Date'),
        'company_id': fields.many2one('res.company', u'Company'),
        'currency_id': fields.many2one('res.currency', 'Currency'),
        'aaw_id': fields.many2one(
            'account.aging.wizard',
            'Account Aging Wizard',
            help='Account Aging Wizard Holder'),
        'aawp_id': fields.many2one(
            'account.aging.wizard.partner',
            'Account Aging Wizard Partner',
            help='Account Aging Wizard Partner'),
    }


class AccountAgingWizardPartner(osv.osv_memory):
    _name = 'account.aging.wizard.partner'
    _description = 'Account Aging Wizard Partner'
    _rec_name = 'partner_id'
    _order = 'name'

    def _get_amount(self, cr, uid, ids, field_names, arg, context=None):
        context = dict(context or {})
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            direction = line.aaw_id.direction == 'past'
            spans = [line.aaw_id.period_length * x * (direction and 1 or -1)
                     for x in range(5)]
            res[line.id] = dict((fn, 0.0) for fn in field_names)
            for doc in line.document_ids:
                if 'residual' in field_names:
                    res[line.id]['residual'] += doc.residual
                if 'payment' in field_names:
                    res[line.id]['payment'] += doc.payment
                if 'total' in field_names:
                    res[line.id]['total'] += doc.total

                if 'not_due' in field_names and not direction:
                    # We will use same field not due to store all due amounts
                    if doc.due_days > 0:
                        res[line.id]['not_due'] += doc.residual
                if 'span01' in field_names and not direction:
                    if doc.due_days <= 0 and doc.due_days > spans[1]:
                        res[line.id]['span01'] += doc.residual
                if 'span02' in field_names and not direction:
                    if doc.due_days <= spans[1] and doc.due_days > spans[2]:
                        res[line.id]['span02'] += doc.residual
                if 'span03' in field_names and not direction:
                    if doc.due_days <= spans[2] and doc.due_days > spans[3]:
                        res[line.id]['span03'] += doc.residual
                if 'span04' in field_names and not direction:
                    if doc.due_days <= spans[3] and doc.due_days > spans[4]:
                        res[line.id]['span04'] += doc.residual
                if 'span05' in field_names and not direction:
                    if doc.due_days <= spans[4]:
                        res[line.id]['span05'] += doc.residual

                if 'not_due' in field_names and direction:
                    if doc.due_days <= 0:
                        res[line.id]['not_due'] += doc.residual
                if 'span01' in field_names and direction:
                    if doc.due_days > 0 and doc.due_days <= spans[1]:
                        res[line.id]['span01'] += doc.residual
                if 'span02' in field_names and direction:
                    if doc.due_days > spans[1] and doc.due_days <= spans[2]:
                        res[line.id]['span02'] += doc.residual
                if 'span03' in field_names and direction:
                    if doc.due_days > spans[2] and doc.due_days <= spans[3]:
                        res[line.id]['span03'] += doc.residual
                if 'span04' in field_names and direction:
                    if doc.due_days > spans[3] and doc.due_days <= spans[4]:
                        res[line.id]['span04'] += doc.residual
                if 'span05' in field_names and direction:
                    if doc.due_days > spans[4]:
                        res[line.id]['span05'] += doc.residual

        return res

    def _get_aawp(self, cr, uid, ids, context=None):
        context = dict(context or {})
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.aawp_id.id] = True
        return res.keys()

    _columns = {
        'partner_id': fields.many2one(
            'res.partner', 'Partner',
            required=True,),
        'name': fields.related(
            'partner_id', 'name',
            string='Name',
            type='char',
            store=True),
        'aaw_id': fields.many2one(
            'account.aging.wizard',
            'Account Aging Wizard',
            help='Account Aging Wizard Holder'),
        'document_ids': fields.one2many(
            'account.aging.wizard.document',
            'aawp_id', 'Documents',
            help='Balance by Currency'),
        'aml_ids': fields.many2many(
            'account.move.line',
            'aaw_id', 'Journal Items',
            help='Journal Items'),
        'currency_id': fields.many2one(
            'res.currency', 'Currency',
            required=True,),
        'total': fields.function(
            _get_amount,
            string='Total',
            store={
                _name: (lambda self, cr, uid, ids, cx: ids, [], 15),
                'account.aging.wizard.document': (_get_aawp, [], 15),
            },
            multi='amounts',
            type='float'),
        'payment': fields.function(
            _get_amount,
            string='Payment',
            store={
                _name: (lambda self, cr, uid, ids, cx: ids, [], 15),
                'account.aging.wizard.document': (_get_aawp, [], 15),
            },
            multi='amounts',
            type='float'),
        'residual': fields.function(
            _get_amount,
            string='Residual',
            store={
                _name: (lambda self, cr, uid, ids, cx: ids, [], 15),
                'account.aging.wizard.document': (_get_aawp, [], 15),
            },
            multi='amounts',
            type='float'),
        'not_due': fields.function(
            _get_amount,
            string='Not Due',
            store={
                _name: (lambda self, cr, uid, ids, cx: ids, [], 15),
                'account.aging.wizard.document': (_get_aawp, [], 15),
            },
            multi='amounts',
            type='float'),
        'span01': fields.function(
            _get_amount,
            string='span01',
            store={
                _name: (lambda self, cr, uid, ids, cx: ids, [], 15),
                'account.aging.wizard.document': (_get_aawp, [], 15),
            },
            multi='amounts',
            type='float'),
        'span02': fields.function(
            _get_amount,
            string='span02',
            store={
                _name: (lambda self, cr, uid, ids, cx: ids, [], 15),
                'account.aging.wizard.document': (_get_aawp, [], 15),
            },
            multi='amounts',
            type='float'),
        'span03': fields.function(
            _get_amount,
            string='span03',
            store={
                _name: (lambda self, cr, uid, ids, cx: ids, [], 15),
                'account.aging.wizard.document': (_get_aawp, [], 15),
            },
            multi='amounts',
            type='float'),
        'span04': fields.function(
            _get_amount,
            string='span04',
            store={
                _name: (lambda self, cr, uid, ids, cx: ids, [], 15),
                'account.aging.wizard.document': (_get_aawp, [], 15),
            },
            multi='amounts',
            type='float'),
        'span05': fields.function(
            _get_amount,
            string='span05',
            store={
                _name: (lambda self, cr, uid, ids, cx: ids, [], 15),
                'account.aging.wizard.document': (_get_aawp, [], 15),
            },
            multi='amounts',
            type='float'),
        'aawc_id': fields.many2one(
            'account.aging.wizard.currency',
            'Account Aging Wizard Currency',
            help='Account Aging Wizard Currency Holder'),
    }


class AccountAgingWizardCurrency(osv.osv_memory):
    _name = 'account.aging.wizard.currency'
    _description = 'Account Aging Wizard Currency'
    _rec_name = 'currency_id'

    def _get_amount(self, cr, uid, ids, field_names, arg, context=None):
        context = dict(context or {})
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = dict((fn, 0.0) for fn in field_names)
            for part in line.partner_ids:
                if 'residual' in field_names:
                    res[line.id]['residual'] += part.residual
                if 'not_due' in field_names:
                    res[line.id]['not_due'] += part.not_due
                if 'span01' in field_names:
                    res[line.id]['span01'] += part.span01
                if 'span02' in field_names:
                    res[line.id]['span02'] += part.span02
                if 'span03' in field_names:
                    res[line.id]['span03'] += part.span03
                if 'span04' in field_names:
                    res[line.id]['span04'] += part.span04
                if 'span05' in field_names:
                    res[line.id]['span05'] += part.span05
        return res

    _columns = {
        'currency_id': fields.many2one(
            'res.currency', 'Currency',
            required=True,),
        'aaw_id': fields.many2one(
            'account.aging.wizard',
            'Account Aging Wizard',
            help='Account Aging Wizard Holder'),
        'partner_ids': fields.one2many(
            'account.aging.wizard.partner',
            'aawc_id', 'Partner by Currency',
            help='Partner by Currency'),
        'residual': fields.function(
            _get_amount,
            string='Residual',
            multi='amounts',
            type='float'),
        'not_due': fields.function(
            _get_amount,
            string='Not Due',
            multi='amounts',
            type='float'),
        'span01': fields.function(
            _get_amount,
            string='span01',
            multi='amounts',
            type='float'),
        'span02': fields.function(
            _get_amount,
            string='span02',
            multi='amounts',
            type='float'),
        'span03': fields.function(
            _get_amount,
            string='span03',
            multi='amounts',
            type='float'),
        'span04': fields.function(
            _get_amount,
            string='span04',
            multi='amounts',
            type='float'),
        'span05': fields.function(
            _get_amount,
            string='span05',
            multi='amounts',
            type='float'),
    }


class AccountAgingPartnerWizard(osv.osv_memory):
    _name = 'account.aging.wizard'
    _description = 'Price List'
    _rec_name = 'result_selection'

    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid,
                                                             context=context)
        if not company_id:
            raise osv.except_osv(
                _('Error!'),
                _('There is no default company for the current user!'))
        return company_id

    _columns = {
        'report_format': fields.selection([
            ('pdf', 'PDF'),
            # TODO: enable print on controller to HTML
            # ('html', 'HTML'),
            ('xls', 'Spreadsheet')],
            'Report Format',
            required=True, default='pdf'),
        'result_selection': fields.selection(
            [
                ('supplier', 'Payable'),
                ('customer', 'Receivable')],
            "Target",
            required=True, default='customer'),
        'type': fields.selection(
            [('aging', 'Aging Report'),
             ('detail', 'Detailed Report'),
             ('aging_detail', 'Aging Detailed Report'), ],
            # ('formal', 'Formal Report')],
            "Type",
            required=True, default='aging'),
        'currency_ids': fields.one2many(
            'account.aging.wizard.currency',
            'aaw_id', 'Balance by Currency',
            help='Balance by Currency'),
        'document_ids': fields.one2many(
            'account.aging.wizard.document',
            'aaw_id', 'Document',
            help='Document'),
        'partner_ids': fields.one2many(
            'account.aging.wizard.partner',
            'aaw_id', 'Partners',
            help='Partners'),
        'company_id': fields.many2one(
            'res.company', 'Company', required=True,
            default=lambda s: s._get_default_company()),
        'period_length': fields.integer(
            'Period Length (days)', required=True, default='30'),
        'user_id': fields.many2one('res.users', 'User',
                                   default=lambda s: s._uid),
        'direction': fields.selection(
            [
                ('future', 'Future'),
                ('past', 'Past')],
            "Direction",
            required=True, default='past'),
    }

    def _get_lines_by_partner_without_invoice(
            self, cr, uid, ids, rp_ids, context=None):
        context = dict(context or {})
        wzd_brw = self.browse(cr, uid, ids[0], context=context)
        aml_obj = self.pool.get('account.move.line')
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
        aml_ids = aml_obj.search(cr, uid, args, context=context)
        res = []

        # From here on create a new method that consumes the aml_ids
        # This method make the groupings and return the results ready to be
        # used in the original place where the method was called
        if not aml_ids:
            return []
        aml_rd = aml_obj.read(
            cr, uid, aml_ids, ['partner_id', 'reconcile_partial_id', 'debit',
                               'credit', 'amount_currency', 'currency_id'],
            load=None, context=context)
        try:
            from pandas import DataFrame
        except ImportError:
            _logger.info('aging_due_report is declared '
                         ' from addons-vauxoo '
                         ' you will need: sudo pip install pandas')
        aml_data = DataFrame(aml_rd).set_index('id')
        aml_data_grouped = aml_data.groupby(['partner_id',
                                             'reconcile_partial_id'])

        aml_data_groups = aml_data_grouped.groups

        for key, val in aml_data_groups.iteritems():
            partner_id, reconcile_id = key
            if reconcile_id:
                # TODO: This process can be improve by using the approach reach
                # in commission_payment
                date_due = [amx_brw.date_maturity or amx_brw.date
                            for amx_brw in aml_obj.browse(
                                cr, uid, val, context=context)
                            if amx_brw.journal_id.type in ('sale', 'purchase')]
                date_due = (date_due and min(date_due) or
                            min([amy_brw.date_maturity or amy_brw.date
                                 for amy_brw in aml_obj.browse(
                                     cr, uid, val, context=context)]))
                date_emission = [amz_brw.date
                                 for amz_brw in aml_obj.browse(
                                     cr, uid, val, context=context)
                                 if amz_brw.journal_id.type in (
                                     'sale', 'purchase')]
                date_emission = (date_emission and min(date_emission) or
                                 min([amw_brw.date
                                      for amw_brw in aml_obj.browse(
                                          cr, uid, val, context=context)]))
                aml_id = [amv_brw.id
                          for amv_brw in aml_obj.browse(
                              cr, uid, val, context=context)
                          if (amv_brw.journal_id.type in (
                              'sale', 'purchase') and
                              amv_brw.date == date_emission)]
                aml_id = (aml_id or [
                    amu_brw.id for amu_brw in aml_obj.browse(
                        cr, uid, val, context=context)
                    if amu_brw.date == date_emission])

                doc = {
                    'partner_id': partner_id,
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
            for aml_brw in aml_obj.browse(cr, uid, val, context=context):
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

    def _get_aml(self, cr, uid, ids, inv_type='out_invoice', currency_id=None):
        aml_obj = self.pool.get('account.move.line')
        res = 0.0
        sign = 1 if inv_type == 'out_invoice' else -1
        if not ids:
            return res
        if currency_id:
            aml_gen = (
                aml_brw.amount_currency * sign
                for aml_brw in aml_obj.browse(cr, uid, ids))
            for iii in aml_gen:
                res += iii
        else:
            aml_gen = (
                aml_brw.debit and (aml_brw.debit * sign) or
                aml_brw.credit * (-1 * sign)
                for aml_brw in aml_obj.browse(cr, uid, ids))
            for iii in aml_gen:
                res += iii
        return res

    def _get_invoice_by_partner(self, cr, uid, partner_ids,
                                inv_type='out_invoice', context=None):
        """return a dictionary of dictionaries.
            { partner_id: { values and invoice list } }
        """
        context = dict(context or {})
        res = []
        inv_obj = self.pool.get('account.invoice')
        rp_obj = self.pool.get('res.partner')
        # Filtering Partners by Unique Accounting Partners
        fap_fnc = rp_obj._find_accounting_partner
        inv_ids = set(inv_obj.search(
            cr, uid, [('partner_id', 'child_of', partner_ids),
                      ('type', '=', inv_type),
                      ('residual', '!=', 0),
                      ('state', 'not in', ('cancel', 'draft'))]))
        inv_ids = list(inv_ids)
        if not inv_ids:
            return res

        for inv_brw in inv_obj.browse(cr, uid, inv_ids):
            currency_id = (inv_brw.currency_id.id !=
                           inv_brw.company_id.currency_id.id and
                           inv_brw.currency_id.id)
            payment = self._get_aml(
                cr, uid,
                [aml.id for aml in inv_brw.payment_ids],
                inv_type, currency_id)
            residual = inv_brw.amount_total + payment

            if not residual:
                continue

            date_due = [amx_brw.date_maturity
                        for amx_brw in inv_brw.move_id.line_id
                        if amx_brw.account_id.type in (
                            'receivable', 'payable')]
            date_due = date_due and min(date_due)
            date_due = date_due or inv_brw.date_due or inv_brw.date_invoice

            res.append({
                'invoice_id': inv_brw.id,
                'currency_id': inv_brw.currency_id.id,
                'partner_id': fap_fnc(inv_brw.partner_id).id,
                'payment': payment,
                'residual': residual,
                'total': inv_brw.amount_total,
                'tax': inv_brw.amount_tax,
                'base': inv_brw.amount_untaxed,
                'date_due': date_due,
                'date_emission': inv_brw.date_invoice,
            })

        return res

    def compute_lines(self, cr, uid, ids, partner_ids, context=None):
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        rp_obj = self.pool.get('res.partner')

        # Filtering Partners by Unique Accounting Partners
        fap_fnc = rp_obj._find_accounting_partner
        rp_brws = rp_obj.browse(cr, uid, partner_ids, context=context)
        partner_ids = [fap_fnc(rp_brw).id for rp_brw in rp_brws]
        partner_ids = list(set(partner_ids))

        aawc_obj = self.pool.get('account.aging.wizard.currency')
        aawp_obj = self.pool.get('account.aging.wizard.partner')
        aawd_obj = self.pool.get('account.aging.wizard.document')

        wzd_brw = self.browse(cr, uid, ids[0], context=context)
        if wzd_brw.result_selection == 'customer':
            inv_type = 'out_invoice'
        elif wzd_brw.result_selection == 'supplier':
            inv_type = 'in_invoice'
        rp_brws = rp_obj.browse(cr, uid, partner_ids, context=context)

        wzd_brw.document_ids.unlink()
        wzd_brw.partner_ids.unlink()
        wzd_brw.currency_ids.unlink()
        aawp_ids = {}
        aawc_ids = {}

        for each in self._get_invoice_by_partner(
                cr, uid, partner_ids, inv_type=inv_type, context=context):
            partner_id = each['partner_id']
            currency_id = each['currency_id']
            key_pair = (partner_id, currency_id)
            if not aawc_ids.get(currency_id, False):
                aawc_id = aawc_obj.create(cr, uid, {
                    'aaw_id': wzd_brw.id,
                    'currency_id': currency_id,
                }, context=context)
                aawc_ids[currency_id] = aawc_id
            if not aawp_ids.get(key_pair, False):
                aawp_id = aawp_obj.create(cr, uid, {
                    'aaw_id': wzd_brw.id,
                    'partner_id': partner_id,
                    'currency_id': currency_id,
                    'aawc_id': aawc_ids[currency_id],
                }, context=context)
                aawp_ids[partner_id, currency_id] = aawp_id
            each['aawp_id'] = aawp_ids[partner_id, currency_id]
            each['aaw_id'] = wzd_brw.id
            aawd_obj.create(cr, uid, each, context=context)

        for line in self._get_lines_by_partner_without_invoice(
                cr, uid, ids, partner_ids, context=context):
            partner_id = line['partner_id']
            currency_id = line['currency_id']
            key_pair = (partner_id, currency_id)
            if not aawc_ids.get(currency_id, False):
                aawc_id = aawc_obj.create(cr, uid, {
                    'aaw_id': wzd_brw.id,
                    'currency_id': currency_id,
                }, context=context)
                aawc_ids[currency_id] = aawc_id
            if not aawp_ids.get(key_pair, False):
                aawp_id = aawp_obj.create(cr, uid, {
                    'aaw_id': wzd_brw.id,
                    'partner_id': partner_id,
                    'currency_id': currency_id,
                    'aawc_id': aawc_ids[currency_id],
                }, context=context)
                aawp_ids[partner_id, currency_id] = aawp_id
            line['aawp_id'] = aawp_ids[partner_id, currency_id]
            line['aaw_id'] = wzd_brw.id
            aawd_obj.create(cr, uid, line, context=context)

        return True

    def print_report(self, cr, uid, ids, context=None):
        """To get the date and print the report
        @return : return report
        """
        context = dict(context or {})
        ids = isinstance(ids, (int, long)) and [ids] or ids
        wzd_brw = self.browse(cr, uid, ids[0], context=context)

        self.compute_lines(cr, uid, ids, context.get('active_ids', []),
                           context=context)

        datas = {'active_ids': ids}
        context['active_ids'] = ids
        context['active_model'] = 'account.aging.wizard'

        context['xls_report'] = wzd_brw.report_format == 'xls'
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

        return self.pool['report'].get_action(cr, uid, [], name, data=datas,
                                              context=context)
