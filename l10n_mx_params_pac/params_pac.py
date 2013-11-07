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


class params_pac(osv.Model):
    _name = 'params.pac'

    def _get_method_type_selection(self, cr, uid, context=None):
        if context is None:
            context = {}
        # From module of PAC inherit this function and add new methods
        types = []
        return types

    _columns = {
        'name': fields.char('Name', size=128, required=True,
            help='Name for this param'),
        'url_webservice': fields.char('URL WebService', size=256, required=True,
            help='URL of WebService used for send to sign the XML to PAC'),
        'namespace': fields.char('NameSpace', size=256,
            help='NameSpace of XML of the page of WebService of the PAC'),
        'user': fields.char('User', size=128, help='Name user for login to PAC'),
        'password': fields.char('Password', size=128,
            help='Password user for login to PAC'),
        'method_type': fields.selection(_get_method_type_selection,
            "Type of method", type='char', size=64, required=True),
        'company_id': fields.many2one('res.company', 'Company', required=True,
            help='Company where will configurate this param'),
        'active': fields.boolean('Active', help='Indicate if this param is active'),
        'sequence': fields.integer('Sequence',
            help='If have more of a param, take the param with less sequence'),
        'certificate_link': fields.char('Certificate link', size=256 , 
            help='PAC have a public certificate that is necessary by customers to check the validity of the XML and PDF'),
        # 'link_type': fields.selection([('production','Produccion'),('test','Pruebas')],"Tipo de ligas"),
    }
    _defaults = {
        'active': 1,
        'company_id': lambda s, cr, uid, c: s.pool.get(
            'res.company')._company_default_get(cr, uid, 'params.pac', context=c),
        'sequence': 10,

    }
