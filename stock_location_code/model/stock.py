# coding: utf-8

"""Inherit the stock location model to add a code attribute and make the code
searchable.

New feature: Add the warehouse to location.
e.g. [A012345] Stock(El Dorado)
"""

###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: julio (julio@vauxoo.com)
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

import re

from openerp import api, models


class StockLocation(models.Model):

    """Inherit the stock location model to add a code attribute and make the code
    searchable.
    """

    _inherit = 'stock.location'

    # barcode is between [] e.g. "[1234] location1"
    barcode_re = re.compile(r'\[(?P<barcode>.*?)\]')

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        """Search by barcode or the default way"""
        if args is None:
            args = []
        recs = self.browse()
        if name:
            re_search = self.barcode_re.search(name)
            barcode = re_search.group('barcode') if re_search else name
            recs = self.search([('loc_barcode', '=', barcode)] + args,
                               limit=limit)
        res = recs.name_get() or super(StockLocation, self).name_search(
            name, args=args, operator=operator, limit=limit)
        return res

    @api.model
    def _name_get(self, location):
        """Implements the stock location code in a new feauture, where if the
        location has a reference to a warehouse, the name in a m2o search
        concatenates the code and warehouse to a location if they exist.
        Visually, it's better to know which owns the warehouse location.
        """
        name = super(StockLocation, self)._name_get(location)
        barcode = "[%(barcode)s]" % {'barcode': location.loc_barcode} \
            if location.loc_barcode else ''
        return barcode + ' ' + name if barcode else name
