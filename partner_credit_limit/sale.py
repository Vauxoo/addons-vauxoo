#-*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from openerp.osv import osv
from openerp.tools.translate import _


class sale_order(osv.Model):
    _inherit = "sale.order"

    def check_limit(self, cr, uid, ids, context={}):
        so = self.browse(cr, uid, ids[0], context)
        partner = so.partner_id

        moveline_obj = self.pool.get('account.move.line')
        movelines = moveline_obj.search(cr, uid, [('partner_id', '=', partner.id), ('account_id.type', 'in', [
                                        'receivable', 'payable']), ('state', '<>', 'draft'), ('reconcile_id', '=', False)])
        movelines = moveline_obj.browse(cr, uid, movelines)

        debit, credit = 0.0, 0.0
        debit_maturity, credit_maturity = 0.0, 0.0
        # ~ #~
        for line in movelines:
            if line.date_maturity < time.strftime('%Y-%m-%d') and line.date_maturity != False:
                credit_maturity += line.debit
                debit_maturity += line.credit
            credit += line.debit
            debit += line.credit

        saldo = credit - debit
        saldo_maturity = credit_maturity - debit_maturity

        if (saldo_maturity + so.amount_total) > partner.credit_maturity_limit or (saldo + so.amount_total) > partner.credit_limit:
            if not partner.over_credit:
                if (saldo + so.amount_total) > partner.credit_limit and partner.credit_limit > 0.00:
                    msg = _('Can not validate the Sale Order because it has exceeded the credit limit \nCredit Limit: %s \nCheck the credit limits on Partner') % (
                        partner.credit_limit)
                    #'Can not validate Invoice because Total Invoice is greater than credit_limit: %s\nCheck Partner Accounts or Credit Limits !'%(partner.credit_limit)
                    raise osv.except_osv(_('Credit Over Limits !'), (msg))
                    return False
            else:
                self.pool.get('res.partner').write(cr, uid, [partner.id], {
                                                   'credit_limit': credit - debit + so.amount_total})

            if not partner.maturity_over_credit:
                if (saldo_maturity + so.amount_total) > partner.credit_maturity_limit and partner.credit_maturity_limit > 0.00:
                    #~ msg = 'Can not validate Invoice, Total mature due Amount %s as on %s !\nCheck Partner Accounts or Credit Limits !' % (credit - debit, time.strftime('%Y-%m-%d'))
                    msg = _('Can not validate the Sale Order because it has exceeded the credit limit up to date: %s \nMaturity Amount: %s \nMaturity Credit Limit: %s \nCheck the credit limits on Partner') % (
                        time.strftime('%Y-%m-%d'), saldo_maturity, partner.credit_maturity_limit)

                    raise osv.except_osv(_(
                        'Maturity Credit Over Limits !'), (msg))
                    return False
                else:
                    return True
            else:
                self.pool.get('res.partner').write(cr, uid, [partner.id], {
                                                   'credit_maturity_limit': credit_maturity - debit_maturity + so.amount_total})
                return True
        else:

            return True
