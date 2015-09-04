# -*- encoding: utf-8 -*-
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: hugo@vauxoo.com
#    planned by: Nhomar Hernandez <nhomar@vauxoo.com>
############################################################################
from openerp import models, api
import time
from openerp import exceptions


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.one
    def check_limit(self):
        so = self
        partner = so.partner_id

        if so.payment_term.payment_type != 'credit':
            return True

        moveline_obj = self.env['account.move.line']
        movelines = moveline_obj.search(
            [('partner_id', '=', partner.id),
             ('account_id.type', 'in', ['receivable', 'payable']),
             ('state', '!=', 'draft'), ('reconcile_id', '=', False)])
        movelines = moveline_obj.browse(movelines)

        debit, credit = 0.0, 0.0
        debit_maturity, credit_maturity = 0.0, 0.0

        for line in movelines:
            if line.date_maturity < time.strftime('%Y-%m-%d') and \
             line.date_maturity is not False:
                credit_maturity += line.debit
                debit_maturity += line.credit
            credit += line.debit
            debit += line.credit

        balance = credit - debit
        balance_maturity = credit_maturity - debit_maturity

        if (balance_maturity + so.amount_total) > \
           partner.credit_maturity_limit or (balance + so.amount_total) > \
           partner.credit_limit:
            if not partner.over_credit:
                if (balance + so.amount_total) > partner.credit_limit and \
                   partner.credit_limit > 0.00:
                    msg = ('Can not validate the Sale Order because it has '
                           'exceeded the credit limit \nCredit Limit: %s \n'
                           'Check the credit limits on Partner') %\
                            (partner.credit_limit)
                    # 'Can not validate Invoice because Total Invoice is
                    # greater than credit_limit: %s\nCheck Partner Accounts or
                    # Credit Limits !'%(partner.credit_limit)
                    raise exceptions.Warning(('Credit Over Limits !'), (msg))
                    return False
            else:
                partner.write(
                    {'credit_limit': credit - debit + so.amount_total})

            if not partner.maturity_over_credit:
                if (balance_maturity + so.amount_total) > \
                   partner.credit_maturity_limit and \
                   partner.credit_maturity_limit > 0.00:
                    # ~ msg = 'Can not validate Invoice, Total mature due
                    # Amount %s as on %s !\nCheck Partner Accounts or Credit#
                    # Limits !' % (credit - debit, time.strftime('%Y-%m-%d'))
                    msg = ('Can not validate the Sale Order because it has '
                           'exceeded the credit limit up to date: %s \n'
                           'Maturity Amount: %s \nMaturity Credit Limit: %s \n'
                           'Check the credit limits on Partner') %\
                           (time.strftime('%Y-%m-%d'),
                            balance_maturity, partner.credit_maturity_limit)

                    raise exceptions.Warning(
                        ('Maturity Credit Over Limits !'), (msg))
                    return False
                else:
                    return True
            else:
                partner.write(
                    {'credit_maturity_limit':
                     credit_maturity - debit_maturity + so.amount_total})
                return True
        else:

            return True
