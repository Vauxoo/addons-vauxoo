# coding: utf-8
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
# Credits## ###################################################################
#    Coded by: Yanina Aular <yanina.aular@vauxoo.com>
#    Planified by: Humberto Arocha / Nhomar Hernandez
#    Audited by: Vauxoo C.A.
###############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################

from openerp.osv import osv


class ResCurrency(osv.Model):

    _inherit = "res.currency"

    def exchange(self, cr, uid, ids, from_amount, to_currency_id,
                 from_currency_id, exchange_date, context=None):
        """Exchange an amount between the two currencies. Return the amount
        with the conversion.
        @param from_amount: the amount where the exchange will be done.
        @param to_currency_id: id of the currency to be convert.
        @param from_currency_id: id of the currency from the amount will be
        convert.
        @param exchange_date: date were the exchange will be done, this date
        will indicate the conversio rate to use.
        """
        context = context or {}
        context = dict(context)
        if from_currency_id == to_currency_id:
            return from_amount
        context['date'] = exchange_date
        return self.compute(cr, uid, from_currency_id, to_currency_id,
                            from_amount, context=context)
