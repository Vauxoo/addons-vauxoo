##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C)
#    2004-2010 Tiny SPRL (<http://tiny.be>).
#    2009-2010 Veritos (http://veritos.nl).
#    All Rights Reserved
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

from openerp.osv import osv


class account_invoice_line(osv.Model):
    _inherit = "account.invoice.line"

    def move_line_get(self, cr, uid, invoice_id, context=None):
        res = super(account_invoice_line, self).move_line_get(
            cr, uid, invoice_id, context=context)
        invo_obj = self.pool.get('account.invoice')
        invo_brw = invo_obj.browse(cr, uid, invoice_id, context=context)
        account_exp = []
        account_out = []
        for i in invo_brw.invoice_line:
            if i.product_id:

                account_out.append(
                    i.product_id.categ_id and
                    i.product_id.categ_id.property_stock_account_output_categ
                    and
                    i.product_id.categ_id.property_stock_account_output_categ.
                    id)

                account_exp.append(
                    i.product_id.categ_id and
                    i.product_id.categ_id.property_account_expense_categ and
                    i.product_id.categ_id.property_account_expense_categ.id)

                account_out.append(
                    i.product_id.property_stock_account_output and
                    i.product_id.property_stock_account_output.id)

                account_exp.append(i.product_id.property_account_expense and
                                   i.product_id.property_account_expense.id)

                for dict in res:
                    if dict.get('account_id') in account_out:
                        dict.update({
                            'price_unit': i.product_id.cost_ult,
                            'price': i.product_id.cost_ult * i.quantity
                        })

                    elif dict.get('account_id') in account_exp:
                        dict.update({
                            'price_unit': i.product_id.cost_ult,
                            'price': -(i.product_id.cost_ult * i.quantity)})

        print "res", res
        return res

  # vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
