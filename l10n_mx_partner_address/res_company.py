# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: jorge_nr (jorge_nr@vauxoo.com)
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
from openerp import SUPERUSER_ID

class res_company(osv.Model):
    _inherit = 'res.company'
    
    def _get_address_data(self, cr, uid, ids, field_names, arg, context=None):
        """ Read the 'address' functional fields. """
        if context is None:
            context = {}
        result = {}
        part_obj = self.pool.get('res.partner')
        for company in self.browse(cr, uid, ids, context=context):
            result[company.id] = {}.fromkeys(field_names, False)
            if company.partner_id:
                address_data = part_obj.address_get(cr, SUPERUSER_ID, [company.partner_id.id], adr_pref=['default'])
                if address_data['default']:
                    address = part_obj.read(cr, SUPERUSER_ID, address_data['default'], field_names, context=context)
                    for field in field_names:
                        result[company.id][field] = address[field] or False
        return result

    def _set_address_data(self, cr, uid, company_id, name, value, arg, context=None):
        """ Write the 'address' functional fields. """
        if context is None:
            context = {}
        company = self.browse(cr, uid, company_id, context=context)
        if company.partner_id:
            part_obj = self.pool.get('res.partner')
            address_data = part_obj.address_get(cr, uid, [company.partner_id.id], adr_pref=['default'])
            address = address_data['default']
            if address:
                part_obj.write(cr, uid, [address], {name: value or False}, context=context)
            else:
                part_obj.create(cr, uid, {name: value or False, 'parent_id': company.partner_id.id}, context=context)
        return True
        
    _columns={
        'l10n_mx_street3': fields.function(_get_address_data, fnct_inv=_set_address_data, size=128, type='char', string="No. External", multi='address', help='External number of the partner address'),
        'l10n_mx_street4': fields.function(_get_address_data, fnct_inv=_set_address_data, size=128, type='char', string="No. Internal", multi='address', help='Internal number of the partner address'),
        'l10n_mx_city2': fields.function(_get_address_data, fnct_inv=_set_address_data, size=128, type='char', string="Locality", multi='address', help='Locality configurated for this partner'),
    }

   
