# -*- encoding: utf-8 -*-

"""
Inherit the stock location model to add a code attribute and make the code
searchable.
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

from openerp.osv import osv, fields
import re


class stock_location(osv.Model):

    """
    Inherit the stock location model to add a code attribute and make the code
    searchable.
    """

    _inherit = 'stock.location'
    _columns = {
        'code': fields.char('Code', size=64)
    }

    def name_search(self, cr, user, name='', args=None,
                    operator='ilike', context=None, limit=100):
        args = args or []
        if name:
            ids = self.search(
                cr, user, [('code', '=', name)] + args, limit=limit,
                context=context)
            if not ids:
                ids = set()
                ids.update(self.search(cr, user, args + [(
                    'code', operator, name)], limit=limit, context=context))
                if not limit or len(ids) < limit:
                    # we may underrun the limit because of dupes in the results,
                    # that's fine
                    ids.update(self.search(
                        cr, user, args + [('name', operator, name)],
                        limit=(limit and (limit-len(ids)) or False),
                        context=context))
                ids = list(ids)
            if not ids:
                ptrn = re.compile('(\[(.*?)\])')
                res = ptrn.search(name)
                if res:
                    ids = self.search(
                        cr, user, [('code', '=', res.group(2))] + args,
                        limit=limit, context=context)
        else:
            ids = self.search(cr, user, args, limit=limit, context=context)
        result = self.name_get(cr, user, ids, context=context)
        return result

    def _name_get(self, data_dict, context=None):
        """
        @return dictionary
        """
        context = context or {}
        name = data_dict.get('name', '')
        code = data_dict.get('code', False)
        if code:
            name = '[%s] %s' % (code, name)
        return (data_dict['id'], name)

    def name_get(self, cr, user, ids, context=None):
        """
        overwrite openerp method like the one for product.product model in the
        product module.
        """
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        result = []
        if not len(ids):
            return result
        for location in self.browse(cr, user, ids, context=context):
            mydict = {
                'id': location.id,
                'name': location.name,
                'code': location.code,
            }
            result.append(self._name_get(mydict))
        return result
