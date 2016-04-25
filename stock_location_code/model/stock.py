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

from openerp.osv import osv
import re


class StockLocation(osv.Model):

    """Inherit the stock location model to add a code attribute and make the code
    searchable.
    """

    _inherit = 'stock.location'

    def name_search(self, cr, user, name='', args=None,
                    operator='ilike', context=None, limit=100):
        args = args or []
        if name:
            ids = self.search(
                cr, user, [('loc_barcode', '=', name)] + args, limit=limit,
                context=context)
            if not ids:
                ids = set()
                ids.update(self.search(cr, user, args + [(
                    'loc_barcode', operator, name)],
                    limit=limit,
                    context=context))
                if not limit or len(ids) < limit:
                    # we may underrun the limit because of dupes in the
                    # results, that's fine
                    ids.update(self.search(
                        cr, user, args + [('name', operator, name)],
                        limit=(limit and (limit - len(ids)) or False),
                        context=context))
                ids = list(ids)

            if not ids:
                ptrn = re.compile(r'(\[(.*?)\])')
                res = ptrn.search(name)
                if res:
                    ids = self.search(
                        cr, user, [('loc_barcode', '=', res.group(2))] + args,
                        limit=limit, context=context)
        else:
            ids = self.search(cr, user, args, limit=limit, context=context)
        result = self.name_get(cr, user, ids, context=context)
        return result

    def _name_get(self, cr, uid, location, context=None):
        """Implements the stock location code in a new feauture, where if the
        location has a reference to a warehouse, the name in a m2o search
        concatenates the code and warehouse to a location if they exist.
        Visually, it's better to know which owns the warehouse location.
        """
        wh_obj = self.pool.get('stock.warehouse')
        context = context or {}
        name = super(StockLocation, self)._name_get(cr,
                                                    uid,
                                                    location,
                                                    context=context)
        barcode = ''
        bracket_left = '['
        u_bracket_l = unicode(bracket_left, "utf-8")
        bracket_right = ']'
        u_bracket_r = unicode(bracket_right, "utf-8")
        parenth_left = '('
        u_parenth_l = unicode(parenth_left, "utf-8")
        parenth_right = ')'
        u_parenth_r = unicode(parenth_right, "utf-8")
        if location.loc_barcode:
            barcode = "{bracket_l}{barcode}{bracket_r}".format(
                bracket_l=u_bracket_l,
                barcode=location.loc_barcode.encode("utf-8"),
                bracket_r=u_bracket_r)
        wh_id = self.get_warehouse(cr, uid, location, context=context)
        if wh_id:
            name_wh = wh_obj.browse(cr, uid, wh_id).name
            name = "{loc_name} {parenth_l}{warehouse}{parenth_r}".format(
                loc_name=location.name.encode("utf-8"),
                parenth_l=u_parenth_l,
                warehouse=name_wh.encode("utf-8"),
                parenth_r=u_parenth_r)
            name = unicode(name, "utf-8")
        name = "{barcode_loc} {name}".format(
            barcode_loc=barcode,
            name=name.encode("utf-8"))
        return name
