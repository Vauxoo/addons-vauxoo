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

import time
from openerp.addons.decimal_precision import decimal_precision as dp


class percent_imex(osv.Model):

    """ """

    _name = 'percent.imex'

    _columns = {

        'line_purchase_id': fields.many2one('purchase.order.line', 'Line',
                help='Purchase line to compute apply'),
        'total_with_flete': fields.float('Total with Flete',
                 digits_compute=dp.get_precision(
                     'Cost Imex'),
            help='Compute total with flete'),
        'price_unit_bf_flete': fields.float('Price Unit before Flete',
                digits_compute=dp.get_precision(
                    'Cost Imex'),
            help='Price Unit compute before Flete'),
        'tax_base': fields.float('Tax Base',
                 digits_compute=dp.get_precision('Cost Imex'),
                 help='Tax base is total + currency '),
        'purchase_id': fields.many2one('purchase.order', 'Purchase'),
        'percent_lines': fields.one2many('percent.imex.line',
                'percent_id', 'Percents to Apply', help='Percent to compute'),
        'total_national_expense': fields.float('Total national spending',
                   digits_compute=dp.get_precision(
                       'Cost Imex'),
            help='Sum of all taxes calculated'),
        'cost_unit': fields.float('Cost Unit',
                  digits_compute=dp.get_precision('Cost Imex'),
                  help='Cost unit comput betewen Total national\
                spending, quantity and price '),
        'cost_unit_total': fields.float('Cost Unit Total',
                digits_compute=dp.get_precision(
                    'Cost Imex'),
            help='Compute of cost with cost unit'),
        'cost_qty': fields.float('Total',
                 digits_compute=dp.get_precision('Cost Imex'),
                 help='Compute betewen  Cost unit total ant quantity in the line'),
    }
    _rec_name = 'line_purchase_id'


class percent_imex_line(osv.Model):

    """ """

    _name = 'percent.imex.line'

    _columns = {
        'percent': fields.float('Percent',
                                digits_compute=dp.get_precision('Cost Imex'),
                                help='Percent to compute tax'),
        #'purchase_id':fields.many2one('purchase.order','Purchase'),
        'percent_id': fields.many2one('percent.imex', 'Percent'),
        'date': fields.date('Date', help='Date apply by percent'),
        'amount': fields.float('Amount',
                               digits_compute=dp.get_precision('Cost Imex'),
                               help='Quantity to compute by percent'),
    }

    _rec_name = 'percent'


class national_special_tax(osv.Model):

    """ """

    _name = 'national.special.tax'

    _columns = {
        'name': fields.char('Name', 50, help='Tax name to identified'),
        'percent': fields.float('Percent',
                                digits_compute=dp.get_precision('Cost Imex'),
                                help='Percent tax to importation compute'),
        'date': fields.date('Date', help='Date entered on file'),

    }

    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d'),

    }
