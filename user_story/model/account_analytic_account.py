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

        for id in ids:
            res[id] = 0.00
        return res

    _columns = {
        'invoiceables_hours': fields.function(_get_invoiceables_hours,
                                              type='float',
                                              string='Invoiceable Hours',
                                              help='Total hours to charge'),
    }
