# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    Info (info@vauxoo.com)
############################################################################
#    Coded by: isaac (isaac@vauxoo.com)
#    Coded by: moylop260 (moylop260@vauxoo.com)
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

import time
import netsvc
from osv import fields, osv
from mx import DateTime
from tools import config
from tools.translate import _


class account_invoice(osv.osv):
    _inherit = "account.invoice"

    def check_limit_credit(self, cr, uid, ids, context={}):
        invoice = self.browse(cr, uid, ids[0], context)
        partner = invoice.partner_id
        moveline_obj = self.pool.get('account.move.line')
        movelines = moveline_obj.search(cr, uid, [('partner_id', '=', partner.id), ('account_id.type', 'in', [
                                        'receivable', 'payable']), ('state', '<>', 'draft'), ('reconcile_id', '=', False)])
        movelines = moveline_obj.browse(cr, uid, movelines)
        debit, credit = 0.0, 0.0
        debit_maturity, credit_maturity = 0.0, 0.0

        for line in movelines:
            if line.date_maturity < time.strftime('%Y-%m-%d') and line.date_maturity != False:
                credit_maturity += line.debit
                debit_maturity += line.credit
            credit += line.debit
            debit += line.credit

        saldo = credit - debit
        saldo_maturity = credit_maturity - debit_maturity

        if (saldo_maturity + invoice.amount_total) > partner.credit_maturity_limit or (saldo + invoice.amount_total) > partner.credit_limit:
            if not partner.over_credit:
                if (saldo + invoice.amount_total) > partner.credit_limit and partner.credit_limit > 0.00:
                    msg = _('Can not validate the Invoice because it has exceeded the credit limit \nCredit Limit: %s \nCheck the credit limits on partner') % (
                        partner.credit_limit)
                    #'Can not validate Invoice because Total Invoice is greater than credit_limit: %s\nCheck Partner Accounts or Credit Limits !'%(partner.credit_limit)
                    raise osv.except_osv(_('Credit Over Limits !'), (msg))
                    return False
            else:
                self.pool.get('res.partner').write(cr, uid, [partner.id], {
                                                   'credit_limit': credit - debit + invoice.amount_total})

            if not partner.maturity_over_credit:
                if (saldo_maturity + invoice.amount_total) > partner.credit_maturity_limit and partner.credit_maturity_limit > 0.00:
                    #~ msg = 'Can not validate Invoice, Total mature due Amount %s as on %s !\nCheck Partner Accounts or Credit Limits !' % (credit - debit, time.strftime('%Y-%m-%d'))
                    msg = _('Can not validate the Invoice because it has exceeded the credit limit up to date: %s \nMaturity Amount :%s \nMaturity Credit Limit: %s \nCheck the credit limits on Partner') % (
                        time.strftime('%Y-%m-%d'), saldo_maturity, partner.credit_maturity_limit)
                    raise osv.except_osv(_(
                        'Maturity Credit Over Limits !'), (msg))
                    return False
                else:
                    return True
            else:
                self.pool.get('res.partner').write(cr, uid, [partner.id], {
                                                   'credit_maturity_limit': credit_maturity - debit_maturity + invoice.amount_total})
                return True
        else:
            return True
account_invoice()
