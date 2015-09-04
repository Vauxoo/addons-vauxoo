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


class AccontInvoice(models.Model):

    _inherit = 'account.invoice'

    @api.one
    def check_limit_credit(self, cr, uid, ids, context={}):
        invoice = self
        partner = invoice.partner_id
        moveline_obj = self.env['account.move.line']
        movelines = moveline_obj.search(
            cr, uid,
            [('partner_id', '=', partner.id),
             ('account_id.type', 'in', ['receivable', 'payable']),
             ('state', '!=', 'draft'), ('reconcile_id', '=', False)])
        movelines = moveline_obj.browse(cr, uid, movelines)
        debit, credit = 0.0, 0.0
        debit_maturity, credit_maturity = 0.0, 0.0

        for line in movelines:
            if line.date_maturity < time.strftime('%Y-%m-%d') and\
             line.date_maturity is not False:
                credit_maturity += line.debit
                debit_maturity += line.credit
            credit += line.debit
            debit += line.credit

        saldo = credit - debit
        saldo_maturity = credit_maturity - debit_maturity

        if (saldo_maturity + invoice.amount_total) > \
            partner.credit_maturity_limit or \
           (saldo + invoice.amount_total) > partner.credit_limit:
            if not partner.over_credit:
                if (saldo + invoice.amount_total) > \
                 partner.credit_limit and partner.credit_limit > 0.00:
                    msg = ('Can not validate the Invoice because it has '
                           'exceeded the credit limit'
                           ' \nCredit Limit: %s \nCheck the credit limits'
                           ' on partner') % (partner.credit_limit)
                    # 'Can not validate Invoice because Total Invoice is
                    # greater than credit_limit: %s\nCheck Partner Accounts
                    # or Credit Limits !'%(partner.credit_limit)
                    raise exceptions.Warning(('Credit Over Limits !'), (msg))
                    return False
            else:
                self.pool.get('res.partner').write(
                    cr, uid, [partner.id],
                    {'credit_limit': credit - debit + invoice.amount_total})

            if not partner.maturity_over_credit:
                if (saldo_maturity + invoice.amount_total) >\
                 partner.credit_maturity_limit and \
                 partner.credit_maturity_limit > 0.00:
                    # ~ msg = 'Can not validate Invoice, Total mature due
                    # Amount %s as on %s !\nCheck Partner Accounts or
                    # Credit Limits !' % (credit - debit,
                    # time.strftime('%Y-%m-%d'))
                    msg = ('Can not validate the Invoice because it has '
                           'exceeded the credit limit up to date: '
                           '%s \nMaturity Amount :%s \nMaturity Credit Limit: '
                           '%s \nCheck the credit limits '
                           'on Partner') % (
                           time.strftime('%Y-%m-%d'),
                           saldo_maturity, partner.credit_maturity_limit)

                    raise exceptions.Warning(
                        ('Maturity Credit Over Limits !'), (msg))
                    return False
                else:
                    return True
            else:
                self.pool.get('res.partner').write(
                    cr, uid, [partner.id],
                    {'credit_maturity_limit': credit_maturity -
                     debit_maturity + invoice.amount_total})
                return True
        else:
            return True


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
