# -*- encoding: utf-8 -*-
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


class res_partner_address(osv.Model):
    _inherit = 'res.partner.address'
    _columns = {
        'code': fields.char('Code', size=64, help='En caso de que la dirección sea de una sucursal, se puede agregar el código de ésta.')
    }

    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=100):
        ids = []
        if not args:
            args = []
        if name:
            ids = self.search(cr, user, [(
                'code', '=', name)] + args, limit=limit, context=context)
            if not ids:
                ids = self.search(cr, user, [(
                    'code', operator, name)] + args, limit=limit, context=context)
        ids += map(lambda a: a[0], super(res_partner_address, self).name_search(
            cr, user, name=name, args=args, operator=operator, context=context, limit=limit))
        ids = set(ids)
        ids = list(ids)
        result = self.name_get(cr, user, ids, context=context)
        return result
