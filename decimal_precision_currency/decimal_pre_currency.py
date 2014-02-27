#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: Maria Gabriela Quilarque  <gabriela@openerp.com.ve>
#    Planified by: Nhomar Hernandez <nhomar@vauxoo.com>
#    Audited by: Maria Gabriela Quilarque  <gabriela@openerp.com.ve>
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##############################################################################
from openerp.osv import fields, osv
from openerp.tools.translate import _

from tools import config
import time
import datetime
import decimal_precision as dp


class res_currency_rate(osv.Model):

    _inherit = "res.currency.rate"
    _columns = {
        'rate': fields.float('Rate',
            digits_compute=dp.get_precision('Currency'), required=True,
            help='The rate of the currency to the currency of rate 1'),
    }


class res_currency(osv.Model):

    def _current_rate(self, cr, uid, ids, name, arg, context=None):
        if context is None:
            context = {}
        res = {}
        if 'date' in context:
            date = context['date']
        else:
            date = time.strftime('%Y-%m-%d')
        date = date or time.strftime('%Y-%m-%d')
        for id in ids:
            cr.execute(
                "SELECT currency_id, rate\
                    FROM res_currency_rate\
                WHERE currency_id = %s\
                AND name <= %s\
                ORDER BY name desc LIMIT 1", (id, date))
            if cr.rowcount:
                id, rate = cr.fetchall()[0]
                res[id] = rate
            else:
                res[id] = 0
        return res

    _inherit = "res.currency"
    _columns = {
        'rate': fields.function(_current_rate, method=True,
            string='Current Rate', digits_compute=dp.get_precision('Currency'),
            help='The rate of the currency to the currency of rate 1'),
        'rounding': fields.float('Rounding factor',
            digits_compute=dp.get_precision('Currency')),

    }
