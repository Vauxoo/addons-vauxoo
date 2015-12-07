# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Vauxoo Consultores (info@vauxoo.com)
############################################################################
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

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError, except_orm
from openerp.models import BaseModel
from openerp.tools import float_compare
import openerp.addons.decimal_precision as dp
import time


class SaleRegisterSession(models.Model):

    _name = 'sale.register.session'

    SALE_SESSION_STATE = [
        ('opening', 'Opening'),
        ('opened', 'In Progress'),
        ('closed', 'Closed'),
    ]

    @api.multi
    @api.depends('name')
    def _compute_cash_all(self):

        for session in self:
            for bank_statement in session.payment_ids:
                if bank_statement.journal_id.cash_control:
                    session.cash_control = True
                    session.cash_journal_id = bank_statement.journal_id.id
                    session.cash_register_id = bank_statement.id

    name = fields.Char(
        'Sale Session',
        required=True,
        default='/')
    user_id = fields.Many2one(
        'res.users', 'Responsible',
        required=True,
        select=1,
        readonly=True,
        states={'opening': [('readonly', False)]}
    )
    state = fields.Selection(
        SALE_SESSION_STATE, 'Status',
        required=True, readonly=True,
        select=1, copy=False, default='opening')
    start_at = fields.Datetime('Opening Date', readonly=True)
    stop_at = fields.Datetime('Closing Date', readonly=True)
    cash_control = fields.Boolean(
        compute='_compute_cash_all',
        string='Has Cash Control')
    cash_journal_id = fields.Many2one(
        'account.journal',
        compute='_compute_cash_all',
        string='Cash Journal', store=True)
    cash_register_id = fields.Many2one(
        'account.bank.statement',
        compute='_compute_cash_all',
        string='Cash Register', store=True)
    opening_details_ids = fields.One2many(
        'account.cashbox.line',
        related='cash_register_id.opening_details_ids',
        string='Opening Cash Control')
    details_ids = fields.One2many(
        'account.cashbox.line',
        related='cash_register_id.details_ids',
        string='Cash Control')
    cash_register_balance_end_real = fields.Float(
        related='cash_register_id.balance_end_real',
        digits_compute=dp.get_precision('Account'),
        string="Ending Balance",
        help="Total of closing cash control lines.",
        readonly=True)
    cash_register_balance_start = fields.Float(
        related='cash_register_id.balance_start',
        digits_compute=dp.get_precision('Account'),
        string="Starting Balance",
        help="Total of opening cash control lines.",
        readonly=True)
    cash_register_total_entry_encoding = fields.Float(
        related='cash_register_id.total_entry_encoding',
        string='Total Cash Transaction',
        readonly=True,
        help="Total of all paid sale orders")
    cash_register_balance_end = fields.Float(
        related='cash_register_id.balance_end',
        digits_compute=dp.get_precision('Account'),
        string="Theoretical Closing Balance",
        help="Sum of opening balance and transactions.",
        readonly=True)
    cash_register_difference = fields.Float(
        related='cash_register_id.difference',
        string='Difference',
        help='Difference between the theoretical closing '
        'balance and the real closing balance.',
        readonly=True)
    sale_ids = fields.One2many(
        'sale.order',
        'session_id',
        'Sale Order',
        readonly=True)
    invoice_ids = fields.One2many(
        'account.invoice',
        'session_id',
        'Invoice',
        readonly=True)
    payment_ids = fields.One2many(
        'account.bank.statement',
        'session_id',
        'Payment',
        readonly=True)

    @api.multi
    @api.constrains('state', 'user_id')
    def _check_unicity(self):
        """
            This method validate only one session opened
            per user
        """
        for session in self:
            domain = [
                ('state', 'not in', ('closed', 'opening')),
                ('user_id', '=', session.user_id.id)
            ]
            count = self.search_count(domain)
            if count > 1:
                raise ValidationError(
                    'You cannot create two active sessions '
                    'with the same responsible!',)

    @api.multi
    def action_open(self):
        for sale_session in self:
            sale_session.write({
                'start_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'state': 'opened'
                })
            for statement_bank in sale_session.payment_ids:
                statement_bank.button_open()
        return True

    @api.multi
    def action_close(self):
        prec = self.env['decimal.precision'].precision_get('Account')
        for sale_session in self:
            transaction_total = 0
            sale_total = 0

            for statement_bank in sale_session.payment_ids:
                transaction_total += statement_bank.total_entry_encoding
                if statement_bank.journal_id.cash_control and\
                        abs(statement_bank.difference):
                    raise except_orm(
                        _('Error!'),
                        _('Your ending balance is too different from '
                          'the theoretical cash closing (%.2f)') % (
                              statement_bank.difference,))

            for order in sale_session.sale_ids:
                sale_total += order.amount_total

            if float_compare(
                    transaction_total, sale_total, precision_digits=prec):

                raise except_orm(
                    _('Error!'),
                    _('Your payment transaction (%.2f) must be '
                      'the same of the sale order (%.2f)') % (
                          transaction_total, sale_total))
            sale_session.write({
                'stop_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'state': 'closed'
                })
        return True

    @api.model
    def create(self, values):
        res = super(SaleRegisterSession, self).create(values)
        res._update_session()
        return res

    @api.multi
    def _update_session(self):
        for session in self:
            journal_ids = self.env['account.journal'].search([
                ('type', '=', 'cash'), ('cash_control', '=', True)
            ])
            for journal in journal_ids:
                bank_statement = {
                    'journal_id': journal.id,
                    'user_id': self._uid,
                    'session_id': session.id
                }
                self.env['account.bank.statement'].create(bank_statement)
            session.write({
                'name': self.env['ir.sequence'].get('sale.register.session')})


@api.model
def default_get(self, field_list):
    """
        This method of BaseModel is overwrite
        to set default value session_id in all
        models with field Many2one to model
        sale.register.session
    """
    defaults = default_get.origin(self, field_list)
    for key, value in self._columns.iteritems():
        if value._obj == 'sale.register.session':
            sale_session = self.env['sale.register.session']
            session_id = sale_session.search(
                [('state', '=', 'opened'), ('user_id', '=', self._uid)])
            defaults.update({key: session_id.id})
    return defaults
BaseModel._patch_method('default_get', default_get)


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    session_id = fields.Many2one(
        'sale.register.session',
        string='Sale Session',
        ondelete='restrict',
        readonly=True)


class AccountBankStatement(models.Model):

    _inherit = 'account.bank.statement'

    session_id = fields.Many2one(
        'sale.register.session',
        string='Sale Session',
        ondelete='restrict',
        readonly=True)


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    session_id = fields.Many2one(
        'sale.register.session',
        string='Sale Session',
        ondelete='restrict',
        readonly=True)
