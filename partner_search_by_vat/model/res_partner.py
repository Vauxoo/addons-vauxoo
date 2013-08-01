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
#

from openerp.osv import fields, osv


class res_partner(osv.osv):

    _inherit = 'res.partner'

    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if context is None:
            context = {}
        res = super(res_partner, self).name_search(
            cr, user, name, args, operator, context, limit)
        if name:
            ids = self.search(
                cr, user, [('vat', operator, name)] + args, limit=limit, context=context)
            res_new = self.name_get(cr, user, ids, context=context)
            res.extend(res_new)
        return res
        
    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return []
        reads = self.read(cr, uid, ids, ['name', 'vat'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['vat']:
                name = '['+record['vat']+'] '+name
            res.append((record['id'], name))
        return res
