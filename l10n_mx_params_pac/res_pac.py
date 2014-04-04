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

    _columns = {
        'name': fields.char('Name', size=128, required=True,
            help='Name for this res pac'),
        'code': fields.char('Code', size=128, help='Code for this res pac'),
        'name_driver': fields.selection('Driver', [('pac_va','Multipac Vauxoo'),('pac_sf','Pac SF'),('pac_finkok','Pac Finkok')], required=True),
        'params_pac_id': fields.many2one('params.pac', 'Params Pac', help="The params pac configuration for this res pac"),
        'company_id': fields.many2one('res.company', 'Company', required=True,
            help='Company where will configurate this param'), 
    }
    
    _defaults = {
        'company_id': lambda s, cr, uid, c: s.pool.get(
            'res.company')._company_default_get(cr, uid, 'params.pac', context=c),
    }
