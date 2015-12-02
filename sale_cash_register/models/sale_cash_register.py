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

from openerp import models, fields, api
from openerp.exceptions import ValidationError
from openerp.models import BaseModel
import time


class SaleRegisterSession(models.Model):

    _name = 'sale.register.session'

    SALE_SESSION_STATE = [
        ('opening', 'Opening'),
        ('opened', 'In Progress'),
        ('closed', 'Closed'),
    ]

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
    picking_ids = fields.One2many(
        'stock.picking',
        'session_id',
        'picking',
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
        return True

    @api.multi
    def action_close(self):
        for sale_session in self:
            sale_session.write({
                'stop_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'state': 'closed'
                })
        return True

    @api.model
    def create(self, values):
        values.update({
            'name': self.env['ir.sequence'].get('sale.register.session')
        })
        return super(SaleRegisterSession, self).create(values)


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


class StockPicking(models.Model):

    _inherit = 'stock.picking'

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
