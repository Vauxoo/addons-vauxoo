# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from openerp.osv import fields, osv


class account_analytic_account(osv.Model):
    _inherit = "account.analytic.account"

    def _remaining_hours_calc(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for account in self.browse(cr, uid, ids, context=context):
            if account.quantity_max != 0:
                res[account.id] = account.quantity_max - \
                    account.invoiceables_hours
            else:
                res[account.id] = 0.0
            res[account.id] = round(res.get(account.id, 0.0), 2)
        return res

    def _get_invoiceables_hours(self, cr, uid, ids, args,
                                fields, context=None):
        if context is None:
            context = {}
        res = {}
        total = 0
        for id in ids:
            acl_obj = self.pool.get('account.analytic.line')
            acl_srch = acl_obj.search(cr, uid, [('account_id', '=', id)])
            acl_brw = acl_obj.browse(cr, uid, acl_srch)
            for acl in acl_brw:
                if acl.to_invoice:
                    total = total + (acl.unit_amount -
                                     (acl.unit_amount *
                                      (acl.to_invoice.factor/100)))
            res[id] = total
        return res

    _columns = {
        'invoiceables_hours': fields.function(_get_invoiceables_hours,
                                              type='float',
                                              string='Units Invoiceable',
                                              help='Total units of hours to \
                                              charge.'),
        'remaining_hours': fields.function(_remaining_hours_calc, type='float',
                                           string='Remaining Time',
                                           help="Computed using the formula: \
                                           Maximum Time - Total Worked Time"),
    }
