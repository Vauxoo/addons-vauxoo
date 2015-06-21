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


from openerp.osv import osv
from openerp.tools.translate import _
from openerp import netsvc
from openerp.tools.safe_eval import safe_eval as eval # pylint: disable=W0622


class account_invoice_refund(osv.osv_memory):

    """Refunds invoice"""
    _inherit = 'account.invoice.refund'

    def _get_journal(self, cr, uid, context=None):
        aj_obj = self.pool.get('account.journal')
        user_obj = self.pool.get('res.users')
        context = context or {}
        itype = context.get('type', 'out_invoice')
        company_id = user_obj.browse(
            cr, uid, uid, context=context).company_id.id
        ttype = (itype == 'out_invoice') and 'sale_refund' or \
               (itype == 'out_refund') and 'sale' or \
               (itype == 'in_invoice') and 'purchase_refund' or \
               (itype == 'in_refund') and 'purchase'
        journal = aj_obj.search(cr, uid, [('type', '=', ttype), (
            'company_id', '=', company_id)], limit=1, context=context)
        return journal and journal[0] or False

    def fields_view_get(self, cr, uid, view_id=None, view_type=False,
                        context=None, toolbar=False, submenu=False):
        if context is None:
            context = {}
        journal_obj = self.pool.get('account.journal')
        user_obj = self.pool.get('res.users')
        # remove the entry with key 'form_view_ref', otherwise fields_view_get
        # crashes
        context.pop('form_view_ref', None)
        res = super(account_invoice_refund, self).\
            fields_view_get(cr, uid,
                            view_id=view_id,
                            view_type=view_type,
                            context=context,
                            toolbar=toolbar, submenu=submenu)
        ttype = context.get('type', 'out_invoice')
        company_id = user_obj.browse(
            cr, uid, uid, context=context).company_id.id
        journal_type = (ttype == 'out_invoice') and 'sale_refund' or \
                       (ttype == 'out_refund') and 'sale' or \
                       (ttype == 'in_invoice') and 'purchase_refund' or \
                       (ttype == 'in_refund') and 'purchase'
        for field in res['fields']:
            if field == 'journal_id':
                journal_select = journal_obj._name_search(cr, uid, '',
                                                          [('type', '=',
                                                            journal_type),
                                                           ('company_id',
                                                               'child_of',
                                                               [company_id])],
                                                          context=context)
                res['fields'][field]['selection'] = journal_select
        return res

    def _get_period(self, cr, uid, context=None):
        """
        Return  default account period value
        """
        account_period_obj = self.pool.get('account.period')
        ids = account_period_obj.find(cr, uid, context=context)
        period_id = False
        if ids:
            period_id = ids[0]
        return period_id

    def _get_orig(self, cr, uid, inv, context=None):
        """
        Return  default origin value
        """
        nro_ref = ''
        if inv.type == 'out_invoice':
            nro_ref = inv.number
        orig = _('INV REFUND:') + (nro_ref or '') + _('- DATE:') + (
            inv.date_invoice or '') + (' TOTAL:' + str(inv.amount_total) or '')
        return orig

    def compute_refund(self, cr, uid, ids, mode='refund', context=None):
        """
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: the account invoice refund’s ID or list of IDs

        """
        ai_obj = self.pool.get('account.invoice')
        reconcile_obj = self.pool.get('account.move.reconcile')
        account_m_line_obj = self.pool.get('account.move.line')
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        wf_service = netsvc.LocalService('workflow')
        inv_tax_obj = self.pool.get('account.invoice.tax')
        ail_obj = self.pool.get('account.invoice.line')
        res_users_obj = self.pool.get('res.users')
        if context is None:
            context = {}

        for form in self.browse(cr, uid, ids, context=context):
            created_inv = []
            date = False
            period = False
            description = False
            company = res_users_obj.browse(
                cr, uid, uid, context=context).company_id
            journal_id = form.journal_id.id
            ivx = None
            for ivx in ai_obj.browse(cr, uid, context.get('active_ids'),
                                      context=context):
                if ivx.state in ['draft', 'proforma2', 'cancel']:
                    raise osv.except_osv(_('Error!'), _(
                        'Cannot %s draft/proforma/cancel invoice.') % (mode))
                if ivx.reconciled and mode in ('cancel', 'modify'):
                    raise osv.except_osv(_('Error!'), _(
                        'Cannot %s invoice which is already reconciled, '
                        'invoice should be unreconciled first. You can only '
                        'refund this invoice.') % (mode))
                if form.period.id:
                    period = form.period.id
                else:
                    period = ivx.period_id and ivx.period_id.id or False

                if not journal_id:
                    journal_id = ivx.journal_id.id

                if form.date:
                    date = form.date
                    if not form.period.id:
                        cr.execute("select name from ir_model_fields \
                                        where model = 'account.period' \
                                        and name = 'company_id'")
                        result_query = cr.fetchone()
                        if result_query:
                            cr.execute("""select p.id from account_fiscalyear y
                                            , account_period p
                                            where y.id=p.fiscalyear_id \
                                and date(%s) between p.date_start AND
                                p.date_stop and y.company_id = %s limit 1""",
                                      (date, company.id,))
                        else:
                            cr.execute("""SELECT id
                                    from account_period where date({date})
                                    between date_start AND  date_stop  \
                                    limit 1 """.format(date=date))
                        rex = cr.fetchone()
                        if rex:
                            period = rex[0]
                else:
                    date = ivx.date_invoice
                if form.description:
                    description = form.description
                else:
                    description = ivx.name

                if not period:
                    raise osv.except_osv(_('Insufficient Data!'),
                                         _('No period found on the invoice.'))

                refund_id = ai_obj.refund(cr, uid, [
                                           ivx.id], date, period,
                                           description, journal_id,
                                           context=context)
                refund = ai_obj.browse(cr, uid, refund_id[0], context=context)
                # Add parent invoice
                ai_obj.write(cr, uid, [refund.id],
                              {'date_due': date,
                               'check_total': ivx.check_total,
                               'parent_id': ivx.id})
                ai_obj.button_compute(cr, uid, refund_id)

                created_inv.append(refund_id[0])
                if mode in ('cancel', 'modify'):
                    movelines = ivx.move_id.line_id
                    to_reconcile_ids = {}
                    for line in movelines:
                        if line.account_id.id == ivx.account_id.id:
                            to_reconcile_ids[line.account_id.id] = [line.id]
                        if type(line.reconcile_id) != osv.orm.browse_null:
                            reconcile_obj.unlink(cr, uid, line.reconcile_id.id)
                    wf_service.trg_validate(uid, 'account.invoice',
                                            refund.id, 'invoice_open', cr)
                    refund = ai_obj.browse(
                        cr, uid, refund_id[0], context=context)
                    for tmpline in refund.move_id.line_id:
                        if tmpline.account_id.id == ivx.account_id.id:
                            to_reconcile_ids[
                                tmpline.account_id.id].append(tmpline.id)
                    for account in to_reconcile_ids:
                        account_m_line_obj.reconcile(
                            cr, uid, to_reconcile_ids[account],
                            writeoff_period_id=period,
                            writeoff_journal_id=ivx.journal_id.id,
                            writeoff_acc_id=ivx.account_id.id
                        )
                    if mode == 'modify':
                        invoice = ai_obj.read(cr, uid, [ivx.id],
                                               ['name', 'type', 'number',
                                                'reference', 'comment',
                                                'date_due', 'partner_id',
                                                'partner_insite',
                                                'partner_contact',
                                                'partner_ref', 'payment_term',
                                                'account_id', 'currency_id',
                                                'invoice_line', 'tax_line',
                                                'journal_id', 'period_id'],
                                               context=context)
                        invoice = invoice[0]
                        del invoice['id']
                        invoice_lines = ail_obj.browse(
                            cr, uid, invoice['invoice_line'], context=context)
                        invoice_lines = ai_obj._refund_cleanup_lines(
                            cr, uid, invoice_lines, context=context)
                        tax_lines = inv_tax_obj.browse(
                            cr, uid, invoice['tax_line'], context=context)
                        tax_lines = ai_obj._refund_cleanup_lines(
                            cr, uid, tax_lines, context=context)
                        invoice.update({
                            'type': ivx.type,
                            'date_invoice': date,
                            'state': 'draft',
                            'number': False,
                            'invoice_line': invoice_lines,
                            'tax_line': tax_lines,
                            'period_id': period,
                            'name': description,
                            'origin': self._get_orig(
                                cr, uid, ivx, context={}),
                        })
                        for field in (
                            'partner_id', 'account_id', 'currency_id',
                                'payment_term', 'journal_id'):
                            invoice[field] = invoice[
                                field] and invoice[field][0]
                        inv_id = ai_obj.create(cr, uid, invoice, {})
                        if ivx.payment_term.id:
                            data = ai_obj.onchange_payment_term_date_invoice(
                                cr, uid, [inv_id], ivx.payment_term.id, date)
                            if 'value' in data and data['value']:
                                ai_obj.write(cr, uid, [inv_id], data['value'])
                        created_inv.append(inv_id)
            xml_id = (ivx.type == 'out_refund') and 'action_invoice_tree1' or \
                     (ivx.type == 'in_refund') and 'action_invoice_tree2' or \
                     (ivx.type == 'out_invoice') and 'action_invoice_tree3' or \
                     (ivx.type == 'in_invoice') and 'action_invoice_tree4'
            result = mod_obj.get_object_reference(cr, uid, 'account', xml_id)
            ids = result and result[1] or False
            result = act_obj.read(cr, uid, ids, context=context)
            invoice_domain = eval(result['domain'])
            invoice_domain.append(('id', 'in', created_inv))
            result['domain'] = invoice_domain
            return result

    def invoice_refund(self, cr, uid, ids, context=None):
        data_refund = self.read(cr, uid, ids, [
                                'filter_refund'],
                                context=context)[0]['filter_refund']
        return self.compute_refund(cr, uid, ids, data_refund, context=context)


account_invoice_refund()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
