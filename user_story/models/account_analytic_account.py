# -*- coding: utf-8 -*-
"""
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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
"""

from openerp import models, fields, api


class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    invoiceables_hours = fields.Float(compute='_get_invoiceables_hours', string='Units Invoiceable',
                                      help='Total units of hours to charge.')
    remaining_hours = fields.Float(compute='_remaining_hours_calc', string='Remaining Time',
                                   help="Computed using the formula: Maximum Time - Total Worked Time")

    def _remaining_hours_calc(self):

        res = {}
        for account in self:
            if account.quantity_max != 0:
                res[account.id] = account.quantity_max - account.invoiceables_hours
            else:
                res[account.id] = 0.0
            res[account.id] = round(res.get(account.id, 0.0), 2)
        return res

    def _get_invoiceables_hours(self):

        res = {}
        total = 0
        for _id in self.ids:
            acl_obj = self.env['account.analytic.line']
            acl_recs = acl_obj.search([('account_id', '=', _id)])
            for acl in acl_recs:
                if acl.to_invoice:
                    total = total + (acl.unit_amount - (acl.unit_amount * (acl.to_invoice.factor / 100)))
            res[_id] = total
        return res
