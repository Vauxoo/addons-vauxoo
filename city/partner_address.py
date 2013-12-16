# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: moylop260 (moylop260@vauxoo.com)
#              Julio Serna (julio@vauxoo.com)
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
from openerp.osv import osv, fields
from openerp import SUPERUSER_ID
from openerp import tools, pooler
from openerp.tools.translate import _

import re
import logging
import pytz
from lxml import etree


class res_partner(osv.Model):
    _inherit = 'res.partner'

    _columns = {
        'city_id': fields.many2one('res.country.state.city', 'City'),
    }

    def fields_view_get(self, cr, user, view_id=None, view_type='form',
                        context=None, toolbar=False, submenu=False):
        if (not view_id) and (view_type == 'form') and context \
            and context.get('force_email', False):
            view_id = self.pool.get('ir.model.data').get_object_reference(
                cr, user, 'base', 'res_partner_form_city_01')[1]
        res = super(res_partner, self).fields_view_get(cr, user,
            view_id, view_type, context, toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            res['arch'] = self.fields_view_get_address(
                cr, user, res['arch'], context=context)
        return res

    def onchange_city(self, cr, uid, ids, city_id, context=None):
        if city_id:
            city = self.pool.get('res.country.state.city').browse(
                cr, uid, city_id, context)
            return {'value': {'city': city.name,
                    'state_id': city.state_id.id,
                    'country_id': city.country_id and city.country_id.id or False}}
        return {}

    def onchange_state_city(self, cr, uid, ids, state_id, city_id, context=None):
        res = super(res_partner, self).onchange_state(cr, uid, ids, state_id, context)
        if city_id and state_id and self.pool.get('res.country.state.city').browse(cr, uid, city_id, context).state_id.id != state_id:
            if res and 'value' in res:
                res['value']['city'] = None
                res['value']['city_id'] = None
        return res

