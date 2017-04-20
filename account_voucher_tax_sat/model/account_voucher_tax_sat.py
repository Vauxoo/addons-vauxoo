# coding: utf-8
###########################################################################
#   Module Writen to OpenERP, Open Source Management Solution
#   Copyright (C) Vauxoo (<http://vauxoo.com>).
#   All Rights Reserved
# ##############Credits######################################################
#   Coded by: Julio Cesar Serna Hernandez(julio@vauxoo.com)
#############################################################################
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################
from openerp import models, fields, api, _
from openerp.exceptions import except_orm


class AccountVoucherTaxSat(models.Model):

    _name = 'account.voucher.tax.sat'

    @api.one
    def _get_date_posted(self):
        period_obj = self.env['account.period']
        period_id = period_obj.next(self.period_id, step=1)

        self.date = period_id.date_start

    name = fields.Char(
        'Name', size=128, help='Name of This Document',)
    partner_id = fields.Many2one(
        'res.partner', 'Partner', domain="[('sat', '=', True)]",
        help='Partner of SAT')
    date = fields.Date(
        compute='_get_date_posted', string='Accounting Date Posted',
        readonly=True, help='Accounting date affected')
    aml_ids = fields.Many2many(
        'account.move.line', 'voucher_tax_sat_rel',
        'voucher_tax_sat_id', 'move_line_id',
        'Move Lines', help='Entries to close')
    aml_iva_ids = fields.Many2many(
        'account.move.line', 'voucher_tax_sat_rel_iva',
        'voucher_sat_id', 'move_line_id',
        'Move Lines', help='Entries IVA to close')
    journal_id = fields.Many2one(
        'account.journal', 'Journal',
        help='Accounting Journal where Entries will be posted')
    move_id = fields.Many2one(
        'account.move', 'Journal Entry',
        help='Accounting Entry')
    company_id = fields.Many2one(
        'res.company', 'Company', help='Company',
        default=lambda self: self.env['res.company']._company_default_get(
            'account.voucher.tax.sat')
    )
    period_id = fields.Many2one(
        'account.period', 'Period', required=True,
        help='Period of Entries to find')
    state = fields.Selection([
        ('draft', 'New'),
        ('cancelled', 'Cancelled'),
        ('done', 'Done')],
        'Status', readonly=True, default='draft')

    @api.onchange('period_id')
    def onchange_period(self):
        self.aml_ids = []
        self.aml_iva_ids = []

    @api.multi
    def validate_move_line(self):
        move_line_obj = self.env['account.move.line']
        self._cr.execute(
            """ SELECT DISTINCT move_line_id
                FROM            voucher_tax_sat_rel
                WHERE           voucher_tax_sat_id <> %s
                AND             move_line_id
                IN              %s
            """, (
                self.id, tuple([move_lines.id for move_lines in self.aml_ids]))
        )
        dat = self._cr.dictfetchall()

        move_line_tax = list(
            set([move_tax['move_line_id']
                 for move_tax in dat]))

        if dat:
            raise except_orm(
                _('Warning'),
                _("You have this jornal items in other voucher tax sat '%s' ")
                % ([move_line.name
                    for move_line in move_line_obj.browse(move_line_tax)]))

        return True

    @api.multi
    def action_close_tax(self):
        period_obj = self.env['account.period']

        period_id = period_obj.find(self.date)

        self.validate_move_line()

        move_id = self.create_move_sat()
        self.write({'move_id': move_id.id})

        currency = self.company_id.currency_id.with_context(
            date=fields.Date.context_today(self))
        amount_tax_sat = currency.round(sum([
            move_line_tax_sat.credit
            for move_line_tax_sat in self.aml_ids]))

        self.create_move_line_sat(self, amount_tax_sat)

        self.create_entries_tax_iva_sat()

        for move_line_tax in self.aml_ids:
            move_line_tax.copy(
                {
                    'move_id': move_id.id,
                    'period_id': period_id.id,
                    'journal_id': self.journal_id.id,
                    'credit': 0.0,
                    'debit': currency.round(move_line_tax.credit),
                    'amount_base': None,
                    'tax_id_secondary': None,
                    'not_move_diot': True,
                    'amount_tax_unround': None
                })

        return self.write({'state': 'done'})

    @api.multi
    def action_cancel(self):
        obj_move_line = self.env['account.move.line']
        if self.move_id:
            obj_move_line._remove_move_reconcile(
                [move_line.id for move_line in self.move_id.line_id])
            self.move_id.button_cancel()
            self.move_id.unlink()
        return self.write({'state': 'draft'})

    @api.multi
    def create_entries_tax_iva_sat(self):
        aml_obj = self.env['account.move.line']
        av_obj = self.env['account.voucher']
        period_obj = self.env['account.period']
        currency = self.company_id.currency_id.with_context(
            date=fields.Date.context_today(self))
        for move_line in self.aml_iva_ids:
            if move_line.tax_id_secondary:
                amount_base, tax_secondary =\
                    av_obj._get_base_amount_tax_secondary(
                        move_line.tax_id_secondary,
                        move_line.amount_base, move_line.credit)
                period_id = period_obj.find(self.date)

                move_line_dt = {
                    'move_id': self.move_id.id,
                    'journal_id': self.journal_id.id,
                    'date': self.date,
                    'period_id': period_id.id,
                    'debit': currency.round(move_line.debit),
                    'name': _('Close of IVA Retained'),
                    'partner_id': move_line.partner_id.id,
                    'account_id':
                    move_line.tax_id_secondary.account_collected_voucher_id.id,
                    'credit': 0.0,
                    'amount_base': amount_base,
                    'tax_id_secondary': tax_secondary
                }
                move_line_cr = {
                    'move_id': self.move_id.id,
                    'journal_id': self.journal_id.id,
                    'date': self.date,
                    'period_id': period_id.id,
                    'debit': 0.0,
                    'name': _('Close of IVA Retained'),
                    'partner_id': move_line.partner_id.id,
                    'account_id': move_line.account_id.id,
                    'credit': currency.round(move_line.debit),
                }
                for line_dt_cr in [move_line_dt, move_line_cr]:
                    aml_obj.create(line_dt_cr)
        return True

    @api.model
    def create_move_line_sat(self, voucher_tax_sat, amount):
        aml_obj = self.env['account.move.line']
        period_obj = self.env['account.period']

        period_id = period_obj.find(voucher_tax_sat.date)

        vals = {
            'move_id': voucher_tax_sat.move_id.id,
            'journal_id': voucher_tax_sat.journal_id.id,
            'date': voucher_tax_sat.date,
            'period_id': period_id.id,
            'debit': 0,
            'name': _('Payment to SAT'),
            'partner_id': voucher_tax_sat.partner_id.id,
            'account_id':
                voucher_tax_sat.partner_id.property_account_payable.id,
            'credit': amount,
        }
        return aml_obj.create(vals)

    @api.multi
    def create_move_sat(self):
        account_move_obj = self.env['account.move']

        vals_move_tax = account_move_obj.account_move_prepare(
            self.journal_id.id,
            date=self.date,
            ref='Entry SAT')
        return account_move_obj.create(vals_move_tax)

    def sat_pay(self, cr, uid, ids, context=None):
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        if not ids:
            return []
        dummy, view_id = self.pool.get('ir.model.data').\
            get_object_reference(
                cr, uid,
                'account_voucher', 'view_vendor_payment_form')
        exp_brw = self.browse(cr, uid, ids[0], context=context)
        return {
            'name': _("Pay SAT"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'account.voucher',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'domain': '[]',
            'context': {
                'default_partner_id': exp_brw.partner_id.id,
                'default_amount': 0.0,
                'close_after_process': True,
                'default_type': 'payment',
                'type': 'payment',
            }
        }
