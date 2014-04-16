# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Sabrina Romero <sabrina@vauxoo.com>  
#    Financed by: Vauxoo Consultores <info@vauxoo.com>
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

import openerp.tools as tools
from openerp.osv import osv, fields

class attachment_client_res_pac_defaults(osv.osv_memory):
    _name = 'attachment.client.res.pac.defaults'

    _columns = {
        'res_pac_id': fields.many2one('res.pac', 'Pac',
                                    help="The pac configuration by default"),
        'user_id': fields.many2one('res.users', 'User Res Pac',
                                    help="The user responsible for this res pac configuration"),
        'company_id': fields.many2one('res.company', 'Company',
                                    help='Company to which it belongs this res pac user'),
    }

    _defaults = {
        'user_id': lambda self, cr, uid, c:
            self.pool.get('res.users').browse(cr, uid, uid, c).id,
        'company_id': lambda self, cr, uid, c:
            self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
    }

    def create_defaults(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        ir_values_obj = self.pool.get('ir.values')
        for res_pac in self.browse(cr, uid, ids, context=None):
            vals = {'name': 'res_pac_id',
                        'key': 'default',
                        'key2': False,
                        'model': 'ir.attachment.facturae.client',
                        'value_unpickle': res_pac.res_pac_id.id,
                        'user_id': res_pac.user_id.id,
                        'company_id': res_pac.company_id.id, }
            ir_values_obj.create(cr, uid, vals, context=None)
