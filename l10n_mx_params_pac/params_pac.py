# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: moylop260 (moylop260@vauxoo.com)
#    Coded by: Isaac Lopez (isaac@vauxoo.com)
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

import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import pooler, tools


class params_pac(osv.osv):
    _name = 'params.pac'

    def _get_method_type_selection(self, cr, uid, context=None):
        #From module of PAC inherit this function and add new methods
        types = []
        return types

    _columns = {
        'name': fields.char('Name', size=128, required=True),
        'url_webservice': fields.char('URL WebService', size=256, required=True),
        'namespace': fields.char('NameSpace', size=256),
        'user': fields.char('User', size=128),
        'password': fields.char('Password', size=128),
        'method_type': fields.selection(_get_method_type_selection,"Type of method", type='char', size=64, required=True),
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'active': fields.boolean('Active'),
        'sequence': fields.integer('Sequence'),

       # 'link_type': fields.selection([('production','Produccion'),('test','Pruebas')],"Tipo de ligas"),
    }
    _defaults = {
        'active': 1,
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'params.pac', context=c),
        'sequence': 10,

    }
params_pac()

