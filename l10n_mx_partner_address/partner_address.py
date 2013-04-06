# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: moylop260 (moylop260@vauxoo.com)
#    Modify by: Juan Carlos Hernandez Funes (juan@vauxoo.com)
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
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
from openerp import pooler, tools
import math
from openerp import SUPERUSER_ID
import re
import logging
import pytz
from lxml import etree

class res_partner(osv.osv):
    _inherit = 'res.partner'

    _columns = {
        'l10n_mx_street3': fields.char('No. Internal', size=128, help='Internal number of the partner address'),
        'l10n_mx_street4': fields.char('No. External', size=128, help='External number of the partner address'),
        'l10n_mx_city2': fields.char('Locality', size=128, help='Locality configurated for this partner'),
    }
    
    def _get_display_address_field(self):
        res = super(res_partner, self)._get_display_address_field()
        res.extend(['l10n_mx_street3','l10n_mx_street4','l10n_mx_city2'])
        return res

    def onchange_address(self, cr, uid, ids, use_parent_address, parent_id, context=None):
        res = super(res_partner, self).onchange_address(cr, uid, ids, use_parent_address, parent_id, context=context)
        def value_or_id(val):
            """ return val or val.id if val is a browse record """
            return val if isinstance(val, (bool, int, long, float, basestring)) else val.id

        if use_parent_address and parent_id:
            parent = self.browse(cr, uid, parent_id, context=context)
            res.get('value', False).update(dict((key, value_or_id(parent[key])) for key in self._get_display_address_field()))
        return res

    def _get_default_country_id(self, cr, uid, context=None):
        country_obj = self.pool.get('res.country')
        #ids = country_obj.search(cr, uid, [ ( 'name', '=', 'México' ), ], limit=1)
        ids = country_obj.search(cr, uid, [ ( 'code', '=', 'MX' ), ], limit=1)
        id = ids and ids[0] or False
        return id

    def fields_view_get_address(self, cr, uid, arch, context={}):
        res = super(res_partner, self).fields_view_get_address(cr, uid, arch, context=context)
        user_obj = self.pool.get('res.users')
        fmt = user_obj.browse(cr, SUPERUSER_ID, uid, context).company_id.country_id
        fmt = fmt and fmt.address_format
        city = '<field name="city" placeholder="City" style="width: 40%%"/>'
        for name, field in self._columns.items():
            if name == 'city_id':
                city = '<field name="city" modifiers="{&quot;invisible&quot;: true}" placeholder="City....." style="width: 50%%"/><field name="city_id" on_change="onchange_city(city_id)" placeholder="City" style="width: 40%%"/>'
                
        layouts = {
            '%(l10n_mx_street3)s\n%(l10n_mx_street4)s\n%(l10n_mx_city2)s': """
                    <group>
                        <group>
                            <label for="type" attrs="{'invisible': [('parent_id','=', False)]}"/>
                            <div attrs="{'invisible': [('parent_id','=', False)]}" name="div_type">
                                <field class="oe_inline"
                                    name="type"/>
                                <label for="use_parent_address" class="oe_edit_only"/>
                                <field name="use_parent_address" class="oe_edit_only oe_inline"
                                    on_change="onchange_address(use_parent_address, parent_id)"/>
                            </div>

                            <label for="street" string="Address"/>
                            <div>
                                <field name="street" placeholder="Street..."/>
                                <field name="street2"/>
                                <field name="l10n_mx_street3" invisible="True" placeholder="No. Interior..."/>
                                <field name="l10n_mx_street4" placeholder="No. Exterior..."/>
                                <div class="address_format">
                                    %s
                                    <field name="state_id" class="oe_no_button" placeholder="State" style="width: 37%%" options='{"no_open": True}' on_change="onchange_state(state_id)"/>
                                    <field name="zip" placeholder="ZIP" style="width: 20%%"/>
                                </div>
                                <field name="l10n_mx_city2" placeholder="Localidad"/>
                                <field name="country_id" placeholder="Country" class="oe_no_button" options='{"no_open": True}'/>
                            </div>
                            <field name="website" widget="url" placeholder="e.g. www.openerp.com"/>
                        </group>
                        <group>
                            <field name="function" placeholder="e.g. Sales Director"
                                attrs="{'invisible': [('is_company','=', True)]}"/>
                            <field name="phone" placeholder="e.g. +32.81.81.37.00"/>
                            <field name="mobile"/>
                            <field name="fax"/>
                            <field name="email" widget="email"/>
                            <field name="title" domain="[('domain', '=', 'contact')]"
                                options='{"no_open": True}' attrs="{'invisible': [('is_company','=', True)]}" />
                        </group>
                    </group>
            """%(city)
        }
        for k,v in layouts.items():
            if fmt and (k in fmt):
                doc = etree.fromstring(res)
                for node in doc.xpath("//form/sheet/group"):
                    tree = etree.fromstring(v)
                    node.getparent().replace(node, tree)
                arch = etree.tostring(doc)
            else:
                arch = res
        return arch

    def fields_view_get(self, cr, user, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        if (not view_id) and (view_type=='form') and context and context.get('force_email', False):
            view_id = self.pool.get('ir.model.data').get_object_reference(cr, user, 'base', 'view_partner_simple_form')[1]
        res = super(res_partner,self).fields_view_get(cr, user, view_id, view_type, context, toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            fields_get = self.fields_get(cr, user, ['l10n_mx_street3','l10n_mx_street4','l10n_mx_city2'], context)
            res['fields'].update(fields_get)
        return res

    _defaults = {
        'country_id': _get_default_country_id,
    }


res_partner()
