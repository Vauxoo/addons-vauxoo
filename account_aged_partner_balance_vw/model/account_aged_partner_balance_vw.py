# -*- encoding: utf-8 -*-
#
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#
#    Coded by: moylop260 (moylop260@vauxoo.com)
#
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
#

from openerp.osv import fields, osv
import openerp.tools as tools
from openerp.tools.translate import _

import openerp.netsvc as netsvc
import time
import os
import mx.DateTime


class account_aged_partner_balance_vw(osv.TransientModel):
    _name = 'account.aged.partner.balance.vw'
    _rec_name = 'partner_id'
    _order = 'partner_id'

    _columns = {
        'partner_id': fields.many2one('res.partner', u'Partner'),
        'total': fields.float(u'Total'),
        'not_due': fields.float(u'Not Due'),
        'days_due_01to30': fields.float(u'01/30'),
        'days_due_31to60': fields.float(u'31/60'),
        'days_due_61to90': fields.float(u'61/90'),
        'days_due_91to120': fields.float(u'91/120'),
        'days_due_121togr': fields.float(u'+121'),
        'company_id': fields.many2one('res.company', u'Company'),
        'currency_company_id':
        fields.many2one('res.currency', u'Company Currency'),
        'aatb_id': fields.many2one('account.aged.trial.balance', ('Aged Trial '
                                                                  'Balance'), help='Aged Trail Balance Document'),
    }


class account_aged_partner_document(osv.TransientModel):
    _name = 'account.aged.partner.document'
    _inherit = 'account.aged.partner.balance.vw'
    _rec_name = 'partner_id'
    _order = 'partner_id, due_days'

    _columns = {
        'user_id':
        fields.many2one('res.users', 'User', help="User's Document"),
        'date_due': fields.date('Due Date', help='Due Date'),
        'due_days': fields.integer(u'Due Days'),
        'residual': fields.float(u'Residual'),
        'aatb_id': fields.many2one('account.aged.trial.balance', ('Aged Trial '
                                                                  'Balance'), help='Aged Trail Balance Document'),
        'document_id': fields.reference('Document',
                                        [('account.invoice', 'Invoice'),
                                         ('account.voucher', 'Voucher'),
                                            ('account.move.line', 'Journal Entry Line')],
                                        size=128,
                                        required=False),
    }


class account_aged_trial_balance(osv.TransientModel):
    _inherit = 'account.aged.trial.balance'

    _columns = {
        'partner_doc_ids': fields.one2many('account.aged.partner.document',
                                           'aatb_id', 'Partner Aged Trail Balance',
                                           help='Partner Aged Trail Balance'),
        'partner_line_ids': fields.one2many('account.aged.partner.balance.vw',
                                            'aatb_id', 'Partner Aged Trail Balance',
                                            help='Partner Aged Trail Balance'),
        'type': fields.selection([('variation', 'Balance Variation in Periods'),
                                  ('distributed', 'Distributed Payments over Debts'),
                                  ('by_document', 'Documents spread in Periods'),
                                  ], 'Type of Report', help='Reporte Type'),
        'state': fields.selection([('draft', 'New'), ('open', 'Open'), ('done', 'Done'),
                                   ], 'Status', help='Document State'),
        'wizard_ids' : fields.one2many('wizard.report.aged.partner.balance', 'aged_trial_report_id')
    }

    _defaults = {
        'state': 'draft',
        'type': 'variation',
    }

    def to_start(self, cr, uid, ids, context=None):
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        wzd_brw = self.browse(cr, uid, ids[0], context=context)
        wzd_brw.write({'state': 'draft', 'partner_line_ids': [(6, 0, [])]})
        return {}

    def aged_report(self, cr, uid, ids, context=None):
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        datas = {'ids': ids}
        wzd_brw = self.browse(cr, uid, ids[0], context=context)
        res = self.check_report(cr, uid, ids, context=context)
        data = res['datas']
        datas['form'] = data['form']
        context.update({'data' : data, 'datas' : datas})
        if wzd_brw.type == 'by_document':
            return {
                    'res_model': 'wizard.report.aged.partner.balance',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'context': context,
                    'type': 'ir.actions.act_window',
                    'target': 'new',
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'account_aged_partner_balance_report',
            'datas': datas,
        }

    def compute_lines(self, cr, uid, ids, context=None):
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        wzd_brw = self.browse(cr, uid, ids[0], context=context)
        wzd_brw.write({'state': 'open', 'partner_line_ids': [(6, 0, [])],
                       'partner_doc_ids': [(6, 0, [])]})
        res = self.check_report(cr, uid, ids, context=context)

        data = res['datas']
        form = data['form']
        self.set_context(cr, uid, ids, data, context=context)
        if wzd_brw.type in ('variation', 'distributed'):
            res = self._get_lines(cr, uid, ids, form, context=context)
            res = map(lambda x: (0, 0, x), res)
            wzd_brw.write({'partner_line_ids': res})
        elif wzd_brw.type == 'by_document':
            res = self._get_doc_lines(cr, uid, ids, form, context=context)
            res = map(lambda x: (0, 0, x), res)
            wzd_brw.write({'partner_doc_ids': res})
        return {}

    def set_context(self, cr, uid, ids, data, context=None):
        context = context or {}
        self.total_account = []
        obj_move = self.pool.get('account.move.line')
        context = data['form'].get('used_context', {})
        context.update({'fiscalyear': False, 'all_fiscalyear': True})
        self.query = obj_move._query_get(cr, uid, obj='l', context=context)
        self.direction_selection = data[
            'form'].get('direction_selection', 'past')
        self.target_move = data['form'].get('target_move', 'all')
        self.date_from = data['form'].get(
            'date_from',
            time.strftime('%Y-%m-%d'))
        if (data['form']['result_selection'] == 'customer'):
            self.ACCOUNT_TYPE = ['receivable']
        elif (data['form']['result_selection'] == 'supplier'):
            self.ACCOUNT_TYPE = ['payable']
        else:
            self.ACCOUNT_TYPE = ['payable', 'receivable']

    def _get_partners(self, cr, uid, ids, form, context=None):
        context = context or {}
        res = []
        wzd_brw = self.browse(cr, uid, ids[0], context=context)
        move_state = ['draft', 'posted']
        if self.target_move == 'posted':
            move_state = ['posted']
        cr.execute('SELECT DISTINCT res_partner.id AS id,\
                    res_partner.name AS name \
                FROM res_partner,account_move_line AS l, account_account, account_move am\
                WHERE (l.account_id=account_account.id) \
                    AND (l.move_id=am.id) \
                    AND (am.state IN %s)\
                    AND (account_account.type IN %s)\
                    AND account_account.active\
                    AND ((reconcile_id IS NULL)\
                       OR (reconcile_id IN (SELECT recon.id FROM account_move_reconcile AS recon WHERE recon.create_date > %s )))\
                    AND (l.partner_id=res_partner.id)\
                    AND (l.date <= %s)\
                    AND ' + self.query + ' \
                ORDER BY res_partner.name', (tuple(move_state), tuple(self.ACCOUNT_TYPE), self.date_from, self.date_from,))
        return cr.dictfetchall()

    def _get_lines(self, cr, uid, ids, form, context=None):
        context = context or {}
        res = []
        wzd_brw = self.browse(cr, uid, ids[0], context=context)
        move_state = ['draft', 'posted']
        if self.target_move == 'posted':
            move_state = ['posted']
        partners = self._get_partners(cr, uid, ids, form, context=context)
        # mise a 0 du total
        for i in range(7):
            self.total_account.append(0)
        #
        # Build a string like (1,2,3) for easy use in SQL query
        partner_ids = [x['id'] for x in partners]
        if not partner_ids:
            return []
        # This dictionary will store the debit-credit for all partners, using
        # partner_id as key.

        type_query = ''
        type_query_r = ''
        if wzd_brw.type == 'distributed':
            if wzd_brw.result_selection == 'customer':
                type_query = ', SUM(l.credit)'
                type_query_r = ', SUM(l.debit)'
            elif wzd_brw.result_selection == 'supplier':
                type_query = ', SUM(l.debit)'
                type_query_r = ', SUM(l.credit)'

        advances = {}

        totals = {}
        cr.execute('SELECT l.partner_id, SUM(l.debit-l.credit) \
                    ' + type_query + '\
                    FROM account_move_line AS l, account_account, account_move am \
                    WHERE (l.account_id = account_account.id) AND (l.move_id=am.id) \
                    AND (am.state IN %s)\
                    AND (account_account.type IN %s)\
                    AND (l.partner_id IN %s)\
                    AND ((l.reconcile_id IS NULL)\
                    OR (l.reconcile_id IN (SELECT recon.id FROM account_move_reconcile AS recon WHERE recon.create_date > %s )))\
                    AND ' + self.query + '\
                    AND account_account.active\
                    AND (l.date <= %s)\
                    GROUP BY l.partner_id ', (tuple(move_state), tuple(self.ACCOUNT_TYPE), tuple(partner_ids), self.date_from, self.date_from,))
        t = cr.fetchall()
        for i in t:
            totals[i[0]] = i[1]
            if wzd_brw.type == 'distributed':
                if wzd_brw.result_selection in ('customer', 'supplier'):
                    advances[i[0]] = i[2]

        # This dictionary will store the future or past of all partners
        future_past = {}
        if self.direction_selection == 'future':
            cr.execute('SELECT l.partner_id, SUM(l.debit-l.credit) \
                        FROM account_move_line AS l, account_account, account_move am \
                        WHERE (l.account_id=account_account.id) AND (l.move_id=am.id) \
                        AND (am.state IN %s)\
                        AND (account_account.type IN %s)\
                        AND (COALESCE(l.date_maturity, l.date) < %s)\
                        AND (l.partner_id IN %s)\
                        AND ((l.reconcile_id IS NULL)\
                        OR (l.reconcile_id IN (SELECT recon.id FROM account_move_reconcile AS recon WHERE recon.create_date > %s )))\
                        AND ' + self.query + '\
                        AND account_account.active\
                    AND (l.date <= %s)\
                        GROUP BY l.partner_id', (tuple(move_state), tuple(self.ACCOUNT_TYPE), self.date_from, tuple(partner_ids), self.date_from, self.date_from,))
            t = cr.fetchall()
            for i in t:
                future_past[i[0]] = i[1]
        # Using elif so people could extend without this breaking
        elif self.direction_selection == 'past':
            cr.execute('SELECT l.partner_id, SUM(l.debit-l.credit) \
                    ' + type_query_r + '\
                    FROM account_move_line AS l, account_account, account_move am \
                    WHERE (l.account_id=account_account.id) AND (l.move_id=am.id)\
                        AND (am.state IN %s)\
                        AND (account_account.type IN %s)\
                        AND (COALESCE(l.date_maturity,l.date) > %s)\
                        AND (l.partner_id IN %s)\
                        AND ((l.reconcile_id IS NULL)\
                        OR (l.reconcile_id IN (SELECT recon.id FROM account_move_reconcile AS recon WHERE recon.create_date > %s )))\
                        AND ' + self.query + '\
                        AND account_account.active\
                    AND (l.date <= %s)\
                        GROUP BY l.partner_id', (tuple(move_state), tuple(self.ACCOUNT_TYPE), self.date_from, tuple(partner_ids), self.date_from, self.date_from,))
            t = cr.fetchall()
            if wzd_brw.type == 'distributed':
                if wzd_brw.result_selection in ('customer', 'supplier'):
                    for i in t:
                        future_past[i[0]] = wzd_brw.result_selection == 'customer' \
                            and i[2] or -(i[2])
                else:
                    for i in t:
                        future_past[i[0]] = i[1]
            else:
                for i in t:
                    future_past[i[0]] = i[1]

        # Use one query per period and store results in history (a list variable)
        # Each history will contain: history[1] = {'<partner_id>':
        # <partner_debit-credit>}
        history = []
        for i in range(5):
            args_list = (
                tuple(move_state),
                tuple(self.ACCOUNT_TYPE),
                tuple(partner_ids),
                self.date_from,
            )
            dates_query = '(COALESCE(l.date_maturity,l.date)'
            if form[str(i)]['start'] and form[str(i)]['stop']:
                dates_query += ' BETWEEN %s AND %s)'
                args_list += (form[str(i)]['start'], form[str(i)]['stop'])
            elif form[str(i)]['start']:
                dates_query += ' > %s)'
                args_list += (form[str(i)]['start'],)
            else:
                dates_query += ' < %s)'
                args_list += (form[str(i)]['stop'],)
            args_list += (self.date_from,)
            cr.execute('''SELECT l.partner_id, SUM(l.debit-l.credit)
                    ''' + type_query_r + '''
                    FROM account_move_line AS l, account_account, account_move am
                    WHERE (l.account_id = account_account.id) AND (l.move_id=am.id)
                        AND (am.state IN %s)
                        AND (account_account.type IN %s)
                        AND (l.partner_id IN %s)
                        AND ((l.reconcile_id IS NULL)
                          OR (l.reconcile_id IN (SELECT recon.id FROM account_move_reconcile AS recon WHERE recon.create_date > %s )))
                        AND ''' + self.query + '''
                        AND account_account.active
                        AND ''' + dates_query + '''
                    AND (l.date <= %s)
                    GROUP BY l.partner_id''', args_list)
            t = cr.fetchall()
            d = {}
            if wzd_brw.type == 'distributed':
                if wzd_brw.result_selection in ('customer', 'supplier'):
                    for i in t:
                        if advances[i[0]] >= i[2]:
                            d[i[0]] = 0.0
                            advances[i[0]] -= i[2]
                        elif advances[i[0]] < i[2] and advances[i[0]]:
                            d[i[0]] = wzd_brw.result_selection == 'customer' \
                                and i[2] - advances[i[0]] or \
                                -(i[2] - advances[i[0]])
                            advances[i[0]] = 0.0
                        else:
                            d[i[0]] = wzd_brw.result_selection == 'customer' \
                                and i[2] or -(i[2])
                else:
                    for i in t:
                        d[i[0]] = i[1]
            else:
                for i in t:
                    d[i[0]] = i[1]
            history.append(d)

        for partner in partners:
            values = {}
            # If choise selection is in the future
            if self.direction_selection == 'future':
                # Query here is replaced by one query which gets the all the
                # partners their 'before' value
                before = False
                if partner['id'] in future_past:
                    before = [future_past[partner['id']]]
                self.total_account[6] = self.total_account[
                    6] + (before and before[0] or 0.0)
                values['direction'] = before and before[0] or 0.0
            # Changed this so people could in the future create new
            # direction_selections
            elif self.direction_selection == 'past':
                # Query here is replaced by one query which gets the all the
                # partners their 'after' value
                after = False
                # Making sure this partner actually was found by the query
                if partner['id'] in future_past:
                    after = [future_past[partner['id']]]

                self.total_account[6] = self.total_account[
                    6] + (after and after[0] or 0.0)
                if wzd_brw.type == 'distributed':
                    if wzd_brw.result_selection in ('customer', 'supplier') and advances.get(partner['id'], 0.0):
                        if advances.get(partner['id'], 0.0) >= (after and after[0] or 0.0):
                            values['direction'] = 0.0
                            advances[partner['id']] -= after and after[
                                0] or 0.0
                        elif advances.get(partner['id'], 0.0) < (after and after[0] or 0.0) and advances.get(partner['id'], 0.0):
                            values['direction'] = wzd_brw.result_selection == 'customer' \
                                and after and after[0] - advances[partner['id']] or \
                                - \
                                (after and after[
                                    0] - advances[partner['id']])
                            advances[partner['id']] = 0.0
                        else:
                            values['direction'] = wzd_brw.result_selection == 'customer' \
                                and after and after[0] or 0.0 or -(after and after[0] or 0.0)
                    else:
                        values['direction'] = after and after[0] or 0.0
                else:
                    values['direction'] = after and after[0] or 0.0

            for i in range(5):
                during = False
                if partner['id'] in history[i]:
                    during = [history[i][partner['id']]]
                # Ajout du compteur
                self.total_account[(i)] = self.total_account[
                    (i)] + (during and during[0] or 0)
                values[str(i)] = during and during[0] or 0.0
            total = False
            if partner['id'] in totals:
                total = [totals[partner['id']]]
            values['total'] = total and total[0] or 0.0
            # Add for total
            self.total_account[(i + 1)] = self.total_account[
                (i + 1)] + (total and total[0] or 0.0)
            values['name'] = partner['name']
            values['partner_id'] = partner['id']

            res.append(values)

        total = 0.0
        totals = {}
        for r in res:
            total += float(r['total'] or 0.0)
            for i in range(5) + ['direction']:
                totals.setdefault(str(i), 0.0)
                totals[str(i)] += float(r[str(i)] or 0.0)
        mapping = {
            'direction': 'not_due',
            '4': 'days_due_01to30',
            '3': 'days_due_31to60',
            '2': 'days_due_61to90',
            '1': 'days_due_91to120',
            '0': 'days_due_121togr',
        }
        res2 = []
        for r in res:
            for j, k in mapping.iteritems():
                r[k] = r.pop(j)
            r.pop('name')
            res2.append(r)
        return res2

    def _get_doc_lines(self, cr, uid, ids, form, context=None):
        context = context or {}
        res = []
        wzd_brw = self.browse(cr, uid, ids[0], context=context)
        partners = self._get_partners(cr, uid, ids, form, context=context)
        partner_ids = [x['id'] for x in partners]
        if not partner_ids:
            return []
        res = self._get_invoice_by_partner(cr, uid, ids, partner_ids)
        res2 = self._get_lines_by_partner_without_invoice(
            cr, uid, ids, partner_ids)
        res += res2
        res = self._screening_invoices(cr, uid, ids, form, res)
        return res

    def _screening_invoices(self, cr, uid, ids, form, res, context=None):
        context = context or {}
        res2 = []
        if not res:
            return []
        for r in res:
            if form['0']['stop'] >= r['date_due']:
                r['days_due_121togr'] = r['residual']
            elif form['1']['start'] <= r['date_due'] and form['1']['stop'] >= r['date_due']:
                r['days_due_91to120'] = r['residual']
            elif form['2']['start'] <= r['date_due'] and form['2']['stop'] >= r['date_due']:
                r['days_due_61to90'] = r['residual']
            elif form['3']['start'] <= r['date_due'] and form['3']['stop'] >= r['date_due']:
                r['days_due_31to60'] = r['residual']
            elif form['4']['start'] <= r['date_due'] and form['4']['stop'] >= r['date_due']:
                r['days_due_01to30'] = r['residual']
            else:
                r['not_due'] = r['residual']
            res2.append(r)
        return res2

    def _get_invoice_by_partner(self, cr, uid, ids, rp_ids, context=None):
        res = []
        context = context or {}
        wzd_brw = self.browse(cr, uid, ids[0], context=context)
        rp_obj = self.pool.get('res.partner')
        inv_obj = self.pool.get('account.invoice')
        args = [
            ('residual', '!=', 0),
            ('state', 'not in', ('cancel', 'draft'))]

        if wzd_brw.result_selection == 'customer':
            args += [('type', '=', 'out_invoice')]
        elif wzd_brw.result_selection == 'supplier':
            args += [('type', '=', 'in_invoice')]
        else:
            return []

        rp_brws = rp_obj.browse(cr, uid, rp_ids, context=context)

        for rp_brw in rp_brws:
            inv_ids = inv_obj.search(
                cr, uid, [('partner_id', '=', rp_brw.id)] + args)
            if not inv_ids:
                continue
            for inv_brw in inv_obj.browse(cr, uid, inv_ids):
                residual = inv_brw.residual
                date_due = mx.DateTime.strptime(
                    inv_brw.date_due or inv_brw.date_invoice, '%Y-%m-%d')
                today = mx.DateTime.strptime(wzd_brw.date_from, '%Y-%m-%d')
                due_days = (today - date_due).day

                if not residual:
                    continue

                res.append({
                    'partner_id': rp_brw.id,
                    'user_id': inv_brw.user_id and inv_brw.user_id.id or False,
                    'document_id': '%s,%s' % (inv_brw._name, inv_brw.id),
                    'residual': residual,
                    'due_days': due_days,
                    'date_due': inv_brw.date_due or inv_brw.date_invoice,
                })
        return res

    def _get_lines_by_partner_without_invoice(
            self, cr, uid, ids, rp_ids, context=None):
        res = []
        context = context or {}
        wzd_brw = self.browse(cr, uid, ids[0], context=context)
        acc_move_line = self.pool.get('account.move.line')
        inv_obj = self.pool.get('account.invoice')
        acc_journal_obj = self.pool.get('account.journal')
        company_id = self.pool.get('res.company')._company_default_get(cr, uid,
                                                                       'account.diot.report', context=context)
        moves_invoice_ids = []
        inv_company = inv_obj.search(
            cr, uid, [('company_id', '=', company_id)], context=context)
        for invoice in inv_obj.browse(cr, uid, inv_company, context=context):
            if invoice.move_id:
                moves_invoice_ids.append(invoice.move_id.id)
        journal_comp = acc_journal_obj.search(
            cr, uid, [('company_id', '=', company_id),
                      ('type', 'in', ['bank', 'cash'])], context=context)
        accounts_journal = []
        for journal in acc_journal_obj.browse(cr, uid, journal_comp, context=context):
            if journal.default_debit_account_id:
                accounts_journal.append(journal.default_debit_account_id.id)
            if journal.default_credit_account_id:
                accounts_journal.append(journal.default_credit_account_id.id)
        accounts_journal = list(set(accounts_journal))
        args = [
            ('reconcile_partial_id', '=', False),
            ('reconcile_id', '=', False),
            ('move_id', 'not in', moves_invoice_ids),
            ('company_id', '=', company_id),
            ('account_id', 'in', accounts_journal),
            ('partner_id', '!=', False)
        ]
        if wzd_brw.direction_selection == 'past':
            args += [('date', '<=', wzd_brw.date_from)]
        elif wzd_brw.direction_selection == 'future':
            args += [('date', '>=', wzd_brw.date_from)]
        if wzd_brw.result_selection == 'customer':
            args += [('credit', '!=', 0)]
        elif wzd_brw.result_selection == 'supplier':
            args += [('debit', '!=', 0)]
        else:
            return []
        move_lines_ret = acc_move_line.search(cr, uid, args, context=context)
        today = mx.DateTime.strptime(wzd_brw.date_from, '%Y-%m-%d')
        for line in acc_move_line.browse(cr, uid, move_lines_ret, context=context):
            date_due = mx.DateTime.strptime(line.date, '%Y-%m-%d')
            due_days = (today - date_due).day
            residual = line.credit or line.debit or False
            res.append({
                'partner_id': line.partner_id and line.partner_id.id or False,
                'user_id': False,
                'document_id': '%s,%s' % (line._name, line.id),
                'residual': residual * -1,
                'due_days': due_days,
                'date_due': line.date,
            })
        return res
