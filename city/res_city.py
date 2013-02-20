# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: moylop260 (moylop260@vauxoo.com)
#              Isaac Lopez (isaac@vauxoo.com)
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

import math
import openerp
from osv import osv, fields
import re
import tools
from tools.translate import _
import logging
from lxml import etree

from openerp.osv import fields, osv

class res_country_state_city(osv.osv):
    _description="Country state city"
    _name = 'res.country.state.city'
    _columns = {
        'name': fields.char('Name', size=64, required=True, select=True, help='Administrative divisions of a state.'),
        'state_id': fields.many2one('res.country.state', 'State',  required=True),
        'country_id': fields.related('state_id','country_id',type='many2one',relation='res.country',string='Country', store=True, readonly=True),
        'code': fields.char('City Code', size=5,
            help='The city code in max. five chars.'),
    }
    _order = 'name'



#~ 
#~ class res_partner(osv.osv):
    #~ _inherit = 'res.partner'
#~ 
    #~ _columns = {
        #~ 'l10n_mx_street3': fields.char('No. Interior', size=128),
        #~ 'l10n_mx_street4': fields.char('No. Exterior', size=128),
        #~ 'l10n_mx_city2': fields.char('Localidad', size=128),
    #~ }
    #~ 
    #~ def _get_address_field(self):
        #~ res = super(res_partner, self)._get_address_field()
        #~ res.extend(['l10n_mx_street3','l10n_mx_street4','l10n_mx_city2'])
        #~ return res
    #~ 
    #~ def _get_default_country_id(self, cr, uid, context=None):
        #~ country_obj = self.pool.get('res.country')
        #~ #ids = country_obj.search(cr, uid, [ ( 'name', '=', 'México' ), ], limit=1)
        #~ ids = country_obj.search(cr, uid, [ ( 'code', '=', 'MX' ), ], limit=1)
        #~ id = ids and ids[0] or False
        #~ return id
#~ 
    #~ def fields_view_get_address(self, cr, uid, arch, context={}):
        #~ res = super(res_partner, self).fields_view_get_address(cr, uid, arch, context=context)
        #~ user_obj = self.pool.get('res.users')
        #~ fmt = user_obj.browse(cr, SUPERUSER_ID, uid, context).company_id.country_id
        #~ fmt = fmt and fmt.address_format
        #~ layouts = {
            #~ '%(l10n_mx_street3)s\n%(l10n_mx_street4)s\n%(l10n_mx_city2)s': """
                    #~ <group>
                        #~ <group>
                            #~ <label for="type" attrs="{'invisible': [('parent_id','=', False)]}"/>
                            #~ <div attrs="{'invisible': [('parent_id','=', False)]}" name="div_type">
                                #~ <field class="oe_inline"
                                    #~ name="type"/>
                                #~ <label for="use_parent_address" class="oe_edit_only"/>
                                #~ <field name="use_parent_address" class="oe_edit_only oe_inline"
                                    #~ on_change="onchange_address(use_parent_address, parent_id)"/>
                            #~ </div>
#~ 
                            #~ <label for="street" string="Address"/>
                            #~ <div>
                                #~ <field name="street" placeholder="Street..."/>
                                #~ <field name="street2"/>
                                #~ <field name="l10n_mx_street3" placeholder="No. Interior..."/>
                                #~ <field name="l10n_mx_street4" placeholder="No. Exterior..."/>
                                #~ <div class="address_format">
                                    #~ <field name="city" placeholder="City" style="width: 40%%"/>
                                    #~ <field name="state_id" class="oe_no_button" placeholder="State" style="width: 37%%" options='{"no_open": True}' on_change="onchange_state(state_id)"/>
                                    #~ <field name="zip" placeholder="ZIP" style="width: 20%%"/>
                                #~ </div>
                                #~ <field name="l10n_mx_city2" placeholder="Localidad"/>
                                #~ <field name="country_id" placeholder="Country" class="oe_no_button" options='{"no_open": True}'/>
                            #~ </div>
                            #~ <field name="website" widget="url" placeholder="e.g. www.openerp.com"/>
                        #~ </group>
                        #~ <group>
                            #~ <field name="function" placeholder="e.g. Sales Director"
                                #~ attrs="{'invisible': [('is_company','=', True)]}"/>
                            #~ <field name="phone" placeholder="e.g. +32.81.81.37.00"/>
                            #~ <field name="mobile"/>
                            #~ <field name="fax"/>
                            #~ <field name="email" widget="email"/>
                            #~ <field name="title" domain="[('domain', '=', 'contact')]"
                                #~ options='{"no_open": True}' attrs="{'invisible': [('is_company','=', True)]}" />
                        #~ </group>
                    #~ </group>
            #~ """
        #~ }
        #~ for k,v in layouts.items():
            #~ if fmt and (k in fmt):
                #~ doc = etree.fromstring(res)
                #~ for node in doc.xpath("//form/sheet/group"):
                    #~ tree = etree.fromstring(v)
                    #~ node.getparent().replace(node, tree)
                #~ arch = etree.tostring(doc)
            #~ else:
                #~ arch = res
        #~ return arch
#~ 
    #~ def fields_view_get(self, cr, user, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        #~ if (not view_id) and (view_type=='form') and context and context.get('force_email', False):
            #~ view_id = self.pool.get('ir.model.data').get_object_reference(cr, user, 'base', 'view_partner_simple_form')[1]
        #~ res = super(res_partner,self).fields_view_get(cr, user, view_id, view_type, context, toolbar=toolbar, submenu=submenu)
        #~ if view_type == 'form':
            #~ fields_get = self.fields_get(cr, user, ['l10n_mx_street3','l10n_mx_street4','l10n_mx_city2'], context)
            #~ res['fields'].update(fields_get)
        #~ return res
    #~ 
    #~ _defaults = {
        #~ 'country_id': _get_default_country_id,
    #~ }


#~ res_partner()
