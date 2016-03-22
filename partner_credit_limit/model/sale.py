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
from openerp import models, api, _
from openerp import exceptions


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def check_limit(self):
        for so in self:
            if so.payment_term.payment_type != 'credit':
                return True
            partner = self.env['res.partner'].with_context(
                {'new_amount': so.amount_total,
                 'new_currency': so.company_id.currency_id.id}).browse(
                     so.partner_id.id)
            if partner.allowed_sale:
                return True
            else:
                msg = 'The Sale order pass to state of Exception Credit.' + \
                    '\nThe partner %s:' % (partner.name)
                if partner.credit_overloaded:
                    msg += ('\nHave exceeded the credit limit.'
                            '\nThe credit available is $%s'
                            '\nAnd the credit is being requested is $%s') % (
                               str((partner.credit_limit - partner.credit)),
                               str(so.amount_total))
                if partner.overdue_credit:
                    moveline_obj = self.env['account.move.line']
                    movelines = moveline_obj.search(
                        [('partner_id', '=', partner.id),
                         ('account_id.type', '=', 'receivable'),
                         ('state', '!=', 'draft'),
                         ('reconcile_id', '=', False)])
                    max_date = max(movelines.mapped('date_maturity'))
                    msg += ('\nIt has the overdue payment period.'
                            '\nThe expiration date was %s, '
                            'the amount payable is: $%s') %(
                            max_date, str(partner.credit))
                message = _(msg)
                raise exceptions.Warning(('Warning!'), message)
