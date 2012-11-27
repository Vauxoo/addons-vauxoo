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

import math
import openerp
from osv import osv, fields
from openerp import SUPERUSER_ID
import re
import tools
from tools.translate import _
import logging
import pooler
import pytz
from lxml import etree

class res_partner(osv.osv):
    _inherit = 'res.partner'

    _columns = {
        'l10n_mx_street3': fields.char('Street3', size=128),
        'l10n_mx_street4': fields.char('Street4', size=128),
        'l10n_mx_city2': fields.char('City2', size=128),
    }

    def _get_default_country_id(self, cr, uid, context=None):
        country_obj = self.pool.get('res.country')
        #ids = country_obj.search(cr, uid, [ ( 'name', '=', 'México' ), ], limit=1)
        ids = country_obj.search(cr, uid, [ ( 'code', '=', 'MX' ), ], limit=1)
        id = ids and ids[0] or False
        return id

    _defaults = {
        'country_id': _get_default_country_id,
    }
res_partner()
