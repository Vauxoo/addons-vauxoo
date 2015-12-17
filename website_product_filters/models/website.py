# coding: utf-8
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C)2010-  OpenERP SA (<http://openerp.com>). All Rights Reserved
#    App Author: Vauxoo
#
#    Coded by Oscar Alcala
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, api
from openerp.http import request


class Website(models.Model):
    _inherit = 'website'

    default_sort = fields.Selection(
        [('name', 'Name'),
         ('pasc', 'Price Lowest'),
         ('pdesc', 'Price Highest'),
         ('hottest', 'Hottest'),
         ('rating', 'Customer Rating'),
         ('popularity', 'Popularity')], defult="popularity")

    @api.model
    def sale_product_domain(self):
        rg_domain = []
        if request.params.get('range', False):
            ranges_obj = self.env['product.price.ranges']
            ranges_list = request.httprequest.args.getlist('range')
            ranges_selected_ids = [int(v) for v in ranges_list if v]
            ranges_selected = ranges_obj.browse(ranges_selected_ids)
            for rang in ranges_selected:
                rg_domain.append(('lst_price', '>=', rang.lower))
                rg_domain.append(('lst_price', '<=', rang.upper))
        domain = super(Website, self).sale_product_domain()
        return domain + rg_domain
