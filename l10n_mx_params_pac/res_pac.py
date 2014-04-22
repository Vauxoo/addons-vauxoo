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

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import pooler, tools

class res_pac(osv.Model):
    _name = 'res.pac'
    
    _rec_name = "name_driver"

    def _get_driver_selection(self, cr, uid, context=None):
        if context is None:
            context = {}
        types = []
        return types

    _columns = {
        'name': fields.char('Name', size=128, required=True,
            help='Name for this res pac'),
        'active': fields.boolean('Active', help='Indicate if this pac is active'),
        'code': fields.char('Code', size=128, help='Code for this res pac'),
        'name_driver': fields.selection(_get_driver_selection, "Pac Driver", type='char', size=64),
        'company_id': fields.many2one('res.company', 'Company', required=True,
            help='Company where will configurate this param'), 
        'user': fields.char('User', size=128, help='Name user for login to PAC'),
        'password': fields.char('Password', size=128, help='Password user for login to PAC'),      
        'url_webservice': fields.char('URL WebService', size=256,
            help='URL of WebService used for send to sign the XML to PAC'),
        'namespace': fields.char('NameSpace', size=256,
            help='NameSpace of XML of the page of WebService of the PAC'),
        'certificate_link': fields.char('Certificate link', size=256 , 
            help='PAC have a public certificate that is necessary by customers to check the validity of the XML and PDF'),
        'params_pac_ids': fields.one2many('params.pac', 'res_pac',
            'Params Pac', help='Params pacs for this Pac'),
    }
    
    _defaults = {
        'company_id': lambda s, cr, uid, c: s.pool.get(
            'res.company')._company_default_get(cr, uid, 'res.pac', context=c),
    }
