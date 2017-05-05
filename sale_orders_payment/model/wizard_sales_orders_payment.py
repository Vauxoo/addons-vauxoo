# -*- coding: utf-8 -*-
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: hugo@vauxoo.com
#    planned by: Nhomar Hernandez <nhomar@vauxoo.com>
############################################################################
from openerp import models, fields, api, _
from openerp import exceptions
from openerp.exceptions import except_orm


class SaleMakePayments(models.TransientModel):
    _name = "sale.make.payments"
    _description = "Sales Make Payments"

    customer_id = fields.Many2one('res.partner', required=True)
    payment_date = fields.Date(default=fields.Date.context_today,
                               required=True)
    line_ids = fields.One2many('sale.make.payments.lines',
                               'sale_make_payment_id')
    amount_to_pay = fields.Float(required=True)
    journal_id = fields.Many2one('account.journal', required=True)

    @api.model
    def view_init(self, fields_list):
        record_ids = self._context and self._context.get('active_ids', False)
        orders = self.env['sale.order'].browse(
            record_ids)
        orders.mapped('state')
        if 'draft' in orders.mapped('state'):
            raise exceptions.Warning(
                _('Warning!'),
                _('You cannot pay sale orders '
                  ' when sales orders is not confirmed.'
                  '\nPlease check Sales Orders selected'))
        return False

    def pay_sale_orders(self, cr, uid, ids, context=None):
        pass

    @api.model
    def default_get(self, fields_list):
        result = super(SaleMakePayments, self).default_get(fields_list)
        sale_ids = self._context.get('active_ids', [])
        active_model = self._context.get('active_model')
        assert active_model in ('sale.order'), 'Bad context propagation'
        sale_orders = self.env['sale.order'].browse(sale_ids)
        customers = sale_orders.mapped('partner_id')
        items = []
        amount_total = 0.0
        if len(customers) > 1:
            raise except_orm(
                _('Error'),
                _('You can not pay Sales Orders of others customers'
                  '\nPlease Select Sales Orders that belong '
                  'to just one Customer'))

        for sale in sale_orders:
            amount_total += sale.amount_total
            item = {
                'sale_id': sale.id,
                'balance': sale.amount_total,
            }
            items.append(item)
        result.update(line_ids=items)
        result.update(amount_to_pay=amount_total)
        result.update(customer_id=customers.id)
        return result


class SaleMakePaymentsLines(models.TransientModel):
    _name = "sale.make.payments.lines"
    _description = "Sales Make Payments Lines"

    sale_make_payment_id = fields.Many2one('sale.make.payments', required=True)
    sale_id = fields.Many2one('sale.order', readonly=True)
    balance = fields.Float(readonly=True)
    amount_to_pay = fields.Float(required=True)
