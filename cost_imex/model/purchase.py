# -*- encoding: utf-8 -*-
##############################################################################
# Copyright (c) 2011 OpenERP Venezuela (http://openerp.com.ve)
# All Rights Reserved.
# Programmed by: Israel Fermín Montilla  <israel@openerp.com.ve>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
###############################################################################
from openerp.osv import fields, osv

from openerp.addons.decimal_precision import decimal_precision as dp


class inherit_purchase(osv.Model):

    """ """

    _inherit = 'purchase.order'

    _columns = {
        'flete': fields.float('Flete',
                  digits_compute=dp.get_precision('Cost Imex'),
                  help='Price to be paid by renting a boat, plane or truck, or\
                cargo carried'),
        'percent_apply': fields.many2many('national.special.tax',
                  'special_national_tax_rel', 'purchase_id', 'special_tax_id',
                  'Percents to Apply', help='Percent to compute'),
        'percent_special': fields.float('Other Percent',
                    digits_compute=dp.get_precision(
                        'Cost Imex'),
            help='Percent to special compute'),
        'import_purchase': fields.boolean('Importation Purchase',
                    help='Indicate if purchase is a importation '),
        'percent_imex_ids': fields.one2many('percent.imex', 'purchase_id',
                    'Percen', domain=[('percent_lines', '!=', False)]),
        'percent_imex_s_ids': fields.one2many('percent.imex', 'purchase_id',
                    'Percen', domain=[('percent_lines', '=', False)]),

    }

    def compute_percent(self, cr, uid, ids, imex_line, order_line, base,
                        context=None):
        if context is None:
            context = {}

        amount = (base * (imex_line.percent / 100))
        imex_lines = {
            'percent': imex_line.percent,
            'date': imex_line.date,
            'amount': amount,

        }

        return imex_lines

    def compute_import_taxes(self, cr, uid, ids, context=None):

        if context is None:
            context = {}
        lines_s = []
        lines = []
        rate = False
        for purchase in self.browse(cr, uid, ids, context=context):
            lines_s = []
            lines = []
            print 'purchase.flete', purchase.flete
            print 'purchase.percent_special', purchase.percent_special
            if purchase.flete and purchase.percent_special:
                for line in purchase.order_line:
                    total_with_flete = (
                        purchase.flete * line.price_subtotal
                    ) + line.price_subtotal

                    if purchase.pricelist_id and\
                        purchase.pricelist_id.currency_id and \
                        purchase.pricelist_id.currency_id.id !=\
                        purchase.company_id and \
                        purchase.company_id.currency_id and \
                            purchase.company_id.currency_id.id:
                        rate = [round((
                            1 / rate.rate), 4)
                            for rate
                            in purchase.pricelist_id.currency_id.rate_ids
                            if rate.name <= purchase.date_order]
                    print 'rate', rate
                    tax_base = total_with_flete * (rate and rate[0] or 1)
                    price_unit_bf_flete = total_with_flete / line.product_qty
                    percent_lines = [(0, 0, self.compute_percent(
                        cr, uid, ids, i, line,
                        tax_base, context=context))
                        for i in purchase.percent_apply]
                    total_national_expense = sum([i[2].get(
                        'amount') for i in percent_lines])
                    cost_unit = (
                        total_national_expense + tax_base) / line.product_qty
                    cost_unit_total = (
                        price_unit_bf_flete + (total_national_expense / (
                                               rate and rate[0] or 1)) / line.product_qty) * (purchase.percent_special)
                    print '(price_unit_bf_flete + (total_national_expense /(rate and rate[0] or 1))/ line.product_qty)', (price_unit_bf_flete + (total_national_expense / (rate and rate[0] or 1)) / line.product_qty)
                    # cost_unit_total =  ((total_with_flete *
                    # purchase.percent_special) + total_national_expense
                    # )/line.product_qty
                    cost_qty = cost_unit_total * line.product_qty
                    lines.append((0, 0, {
                                  'line_purchase_id': line.id,
                                  'total_with_flete': total_with_flete,
                                  'price_unit_bf_flete': price_unit_bf_flete,
                                  'tax_base': tax_base,
                                  'percent_lines': percent_lines,
                                  'total_national_expense': total_national_expense,
                                  'cost_unit': cost_unit,

                                  }
                                  ))

                    lines_s.append((0, 0, {
                                    'line_purchase_id': line.id,
                                    'cost_unit_total': cost_unit_total,
                                    'cost_qty': cost_qty,

                                    }))

                # print 'line',lines
                # print 'line_s',lines_s
                self.write(cr, uid, [purchase.id], {'percent_imex_ids': lines,
                                                    'percent_imex_s_ids': lines_s}, context=context)
        return True
