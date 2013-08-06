# -*- encoding: utf-8 -*-
#
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#
#    Coded by: Fernando Rangel (fernando.rangel@vauxoo.com)
#
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
import math
import re
from openerp.osv import fields, osv


class res_partner(osv.osv):

    _inherit = 'res.partner'

    def name_search(self, cr, user, name, args=None, operator='ilike',
                                                    context=None, limit=100):
        if not args:
            args = []
        if context is None:
            context = {}
        ids = []
        if name:
            ids = self.search(cr, user, [('name', 'ilike', name)]+ args,
                                                limit=limit, context=context)
            if not ids:
                ids = self.search(cr, user, [('vat', 'ilike', name)]+ args,
                                                limit=limit, context=context)
            if not ids:
                ptrn = re.compile('(\[(.*?)\])')
                res = ptrn.search(name)
                if res:
                    ids = self.search(cr, user,
                        [('vat', 'ilike', res.group(2))]+ args, limit=limit,
                                                            context=context)
        return self.name_get(cr, user, ids, context=context)
        
    def name_get(self, cr, uid, ids, context=None):
        if isinstance(ids, (list, tuple)) and not len(ids):
            return []
        if isinstance(ids, (long, int)):
            ids = [ids]
        reads = self.read(cr, uid, ids, ['name', 'vat'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['vat']:
                name = '['+record['vat']+'] '+name
            res.append((record['id'], name))
        return res
