#!/usr/bin/python
# -*- encoding: utf-8 -*-
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
from openerp.addons.aging_due_report.report.parser import aging_parser as ag
from pandas import DataFrame


class account_aging_wizard_document(osv.TransientModel):
    _name = 'account.aging.wizard.document'
    _rec_name = 'partner_id'
    _order = 'partner_id'

    _columns = {
        'partner_id': fields.many2one('res.partner', u'Partner'),
        'invoice_id': fields.many2one('account.invoice', 'Invoice'),
        'residual': fields.float('Residual'),
        'base': fields.float('Base'),
        'tax': fields.float('Tax'),
        'total': fields.float('Total'),
        'payment': fields.float('Payment'),
        'due_days': fields.float('Due Days'),
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


class account_aging_wizard_partner(osv.osv_memory):
    _name = 'account.aging.wizard.partner'
    _description = 'Account Aging Wizard Partner'
    _rec_name = 'partner_id'
    _columns = {
        'partner_id': fields.many2one(
            'res.partner', 'Partner',
            required=True,),
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
            required=False,),
        # TODO: make it required
        # required=True,),
    }


class account_aging_wizard_currency(osv.osv_memory):
    _name = 'account.aging.wizard.currency'
    _description = 'Account Aging Wizard Currency'
    _rec_name = 'currency_id'
    _columns = {
        'currency_id': fields.many2one(
            'res.currency', 'Currency',
            required=True,),
        'aaw_id': fields.many2one(
            'account.aging.wizard',
            'Account Aging Wizard',
            help='Account Aging Wizard Holder'),
    }


class account_aging_partner_wizard(osv.osv_memory):
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
            required=True),
        'result_selection': fields.selection(
            [('customer', 'Receivable'),
             ('supplier', 'Payable')],
            "Target",
            required=True),
        'type': fields.selection(
            [('aging', 'Aging Report'),
             ('detail', 'Detailed Report'),
             ('formal', 'Formal Report')],
            "Type",
            required=True),
        'currency_ids': fields.one2many(
            'account.aging.wizard.currency',
            'aaw_id', 'Balance by Currency',
            help='Balance by Currency'),
        'document_ids': fields.one2many(
            'account.aging.wizard.document',
            'aaw_id', 'Balance by Currency',
            help='Balance by Currency'),
        'partner_ids': fields.one2many(
            'account.aging.wizard.partner',
            'aaw_id', 'Partners',
            help='Partners'),
        'company_id': fields.many2one(
            'res.company', 'Company', required=True),
    }

    _defaults = {
        'report_format': lambda *args: 'xls',
        'result_selection': lambda *args: 'customer',
        'type': lambda *args: 'aging',
        'company_id': _get_default_company,
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
            ('partner_id', 'in', rp_ids)
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
        aml_data = DataFrame(aml_rd).set_index('id')
        aml_data_grouped = aml_data.groupby(['partner_id',
                                            'reconcile_partial_id'])

        aml_data_groups = aml_data_grouped.groups

        for key, val in aml_data_groups.iteritems():
            partner_id, reconcile_id = key
            doc = {
                'partner_id': partner_id,
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
                # 'due_days': due_days,
                'currency_id': False,
                'total': 0.0,
                # 'date_due': aml_brw.date_maturity or aml_brw.date}
                'date_due': False}
            for aml_brw in aml_obj.browse(cr, uid, aml_ids, context=context):
                # ask in this step a read for the aml_ids, this will allow to
                # group later the data
                # TODO: When currency_id is not None then convert values or use
                # other values like amount_currency
                currency_id = (aml_brw.currency_id and aml_brw.currency_id.id or
                            aml_brw.company_id.currency_id.id)
                total = (sel == 'customer' and aml_brw.debit or
                        sel == 'supplier' and aml_brw.credit or 0.0)
                payment = (sel == 'customer' and aml_brw.credit or
                        sel == 'supplier' and aml_brw.debit or 0.0)
                if not reconcile_id:
                    res.append({
                        'partner_id': aml_brw.partner_id.id,
                        # 'wh_vat': wh_vat,
                        # 'wh_islr': wh_islr,
                        # 'wh_muni': wh_muni,
                        # 'wh_src': wh_src,
                        # 'debit_note': debit_note,
                        # 'credit_note': credit_note,
                        # 'refund_brws': refund_brws,
                        'payment': payment,
                        # 'payment_left': payment_left,
                        'residual': (total - payment),
                        # 'due_days': due_days,
                        'currency_id': currency_id,
                        'total': total,
                        'date_due': aml_brw.date_maturity or aml_brw.date})
                else:
                    doc['payment'] += payment
                    doc['total'] += total
                    doc['residual'] += (total - payment)
            if reconcile_id:
                res.append(doc)
        return res

    def compute_lines(self, cr, uid, ids, partner_ids, context=None):
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        rp_obj = self.pool.get('res.partner')
        aawp_obj = self.pool.get('account.aging.wizard.partner')

        wzd_brw = self.browse(cr, uid, ids[0], context=context)
        rp_brws = rp_obj.browse(cr, uid, partner_ids, context=context)
        ag_obj = ag(cr, uid, None, context=context)
        rex = ag_obj._get_invoice_by_currency_group(rp_brws)
        res = []

        wzd_brw.document_ids.unlink()
        wzd_brw.partner_ids.unlink()
        aawp_ids = {}

        # TODO: We have to resolve the issue of multipartners
        for itx in rex:
            for itr in itx:
                for key, val in itr.iteritems():
                    if key == 'inv_ids':
                        for each in val:
                            partner_id = each['partner_id']
                            currency_id = each['currency_id']
                            key_pair = (partner_id, currency_id)
                            if not aawp_ids.get(key_pair, False):
                                aawp_id = aawp_obj.create(cr, uid, {
                                    'aaw_id': wzd_brw.id,
                                    'partner_id': partner_id,
                                    'currency_id': currency_id,
                                }, context=context)
                                aawp_ids[partner_id, currency_id] = aawp_id
                            each['aawp_id'] = aawp_ids[partner_id, currency_id]
                            res.append(each)

        res = [(0, 0, line) for line in res]
        wzd_brw.write({'document_ids': res})
        res = []

        for line in self._get_lines_by_partner_without_invoice(
                cr, uid, ids, partner_ids, context=context):
            partner_id = line['partner_id']
            currency_id = line['currency_id']
            key_pair = (partner_id, currency_id)
            if not aawp_ids.get(key_pair, False):
                aawp_id = aawp_obj.create(cr, uid, {
                    'aaw_id': wzd_brw.id,
                    'partner_id': partner_id,
                    'currency_id': currency_id,
                }, context=context)
                aawp_ids[partner_id, currency_id] = aawp_id
            line['aawp_id'] = aawp_ids[partner_id, currency_id]
            res.append(line)
        res = [(0, 0, line) for line in res]
        wzd_brw.write({'document_ids': res})

        return True

    def print_report(self, cr, uid, ids, context=None):
        """
        To get the date and print the report
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
        if wzd_brw.result_selection == 'customer':
            if wzd_brw.type == 'aging':
                name = 'aging_due_report.aging_due_report_qweb'
            if wzd_brw.type == 'detail':
                name = 'aging_due_report.detail_due_report_qweb'
            if wzd_brw.type == 'formal':
                name = 'aging_due_report.formal_due_report_qweb'
        elif wzd_brw.result_selection == 'supplier':
            if wzd_brw.type == 'aging':
                name = 'aging_due_report.supplier_aging_due_report_qweb'
            if wzd_brw.type == 'detail':
                name = 'aging_due_report.supplier_detail_due_report_qweb'
            if wzd_brw.type == 'formal':
                name = 'aging_due_report.supplier_formal_due_report_qweb'

        return self.pool['report'].get_action(cr, uid, [], name, data=datas,
                                              context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
