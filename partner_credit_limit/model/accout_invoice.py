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
from openerp import models, api, fields, _
import time
from datetime import timedelta
from openerp import exceptions


class AccontInvoice(models.Model):

    _inherit = 'account.invoice'

    @api.one
    def check_limit_credit(self):
        invoice = self
        partner = invoice.partner_id
        moveline_obj = self.env['account.move.line']

        if invoice.payment_term.payment_type != 'credit' or\
                invoice.journal_id.type != 'sale':
            return True
        movelines = moveline_obj.search(
            [('partner_id', '=', partner.id),
             ('account_id.type', '=', 'receivable'),
             ('state', '!=', 'draft'), ('reconcile_id', '=', False)])
        debit, credit = 0.0, 0.0
        debit_maturity, credit_maturity = 0.0, 0.0
        invoice_list = []
        has_late_payment = False

        for line in movelines:
            if line.date_maturity and line.partner_id.grace_payment_days:
                maturity = fields.Datetime.from_string(
                    line.date_maturity)
                grace_payment_days = timedelta(
                    days=line.partner_id.grace_payment_days, seconds=-1)
                limit_day = maturity + grace_payment_days
                limit_day = limit_day.strftime("%Y-%m-%d")

            elif line.date_maturity:
                limit_day = line.date_maturity
                if limit_day < fields.Date.today():
                    if line.amount_residual > 0.0:
                        has_late_payment = True
                        invoice_list.append(line.invoice.number)
                # credit and debit maturity sums all aml with limit date to pay
                credit_maturity += line.debit
                debit_maturity += line.credit
            credit += line.debit
            debit += line.credit

        if has_late_payment:
            msg = _('Can not validate the Invoice because Partner '
                    'has late payments.\nPlease cover the late payment in '
                    'invoices : %s') % (str(invoice_list))
            raise exceptions.Warning((_('Delayed payments!')), msg)

        balance = credit - debit
        # balance_maturity is the balance that must've be paid beafore
        # date_maturity
        balance_maturity = credit_maturity - debit_maturity

        if (balance_maturity + invoice.amount_total) > \
            partner.credit_maturity_limit or \
           (balance + invoice.amount_total) > partner.credit_limit:
            if not partner.over_credit:
                if (balance + invoice.amount_total) > \
                        partner.credit_limit and partner.credit_limit > 0.00:
                    msg = _('Can not validate the Invoice because it has '
                            'exceeded the credit limit'
                            ' \nCredit Limit: %s \nCheck the credit limits'
                            ' on partner') % (partner.credit_limit)
                    # 'Can not validate Invoice because Total Invoice is
                    # greater than credit_limit: %s\nCheck Partner Accounts
                    # or Credit Limits !'%(partner.credit_limit)
                    raise exceptions.Warning(_('Credit Over Limits !'), msg)
            else:
                partner.write(
                    {'credit_limit': credit - debit + invoice.amount_total})

            if not partner.maturity_over_credit:
                if (balance_maturity + invoice.amount_total) >\
                        partner.credit_maturity_limit and \
                        partner.credit_maturity_limit > 0.00:
                    # ~ msg = 'Can not validate Invoice, Total mature due
                    # Amount %s as on %s !\nCheck Partner Accounts or
                    # Credit Limits !' % (credit - debit,
                    # time.strftime('%Y-%m-%d'))
                    msg = _(
                        'Can not validate the Invoice because it has '
                        'exceeded the credit limit up to date: '
                        '%s \nMaturity Amount :%s \nMaturity Credit Limit: '
                        '%s \nCheck the credit limits on Partner') %\
                        (time.strftime('%Y-%m-%d'),
                            balance_maturity, partner.credit_maturity_limit)

                    raise exceptions.Warning(
                        (_('Maturity Credit Over Limits !')), (msg))
                else:
                    return True
            else:
                partner.write(
                    {'credit_maturity_limit': credit_maturity -
                     debit_maturity + invoice.amount_total})
                return True
        else:
            return True


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
