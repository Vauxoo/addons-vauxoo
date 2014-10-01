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
import re
from openerp.osv import osv


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
            ptrn_name = re.compile('(\[(.*?)\])')
            res_name = ptrn_name.search(name)
            if res_name:
                name = name.replace('['+res_name.group(2)+'] ', '')
            partner_search = super(res_partner, self).name_search(cr, user,
                                        name, args, operator, context, limit)
            ids = [partner[0] for partner in partner_search]
            if not ids:
                ids = self.search(cr, user, [('vat', operator, name)]+ args,
                                                limit=limit, context=context)
            if not ids:
                ptrn = re.compile('(\[(.*?)\])')
                res = ptrn.search(name)
                if res:
                    ids = self.search(cr, user,
                        [('vat', operator, res.group(2))]+ args, limit=limit,
                                                            context=context)
        else:
            return super(res_partner, self).name_search(cr, user,
                                        name, args, operator, context, limit)
                                                            
        return self.name_get(cr, user, ids, context=context)
        
    def name_get(self, cr, uid, ids, context=None):
        if isinstance(ids, (list, tuple)) and not len(ids):
            return []
        if isinstance(ids, (long, int)):
            ids = [ids]
        res_name = super(res_partner, self).name_get(cr, uid, ids, context)
        res = []
        for record in res_name:
            partner = self.browse(cr, uid, record[0], context=context)
            name = record[1]
            if partner.vat:
                name = '['+partner.vat+'] '+name
            res.append((record[0], name))
        return res
