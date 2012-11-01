# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: fernandoL (fernando_ld@vauxoo.com)
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

from tools.translate import _
from osv import osv, fields
import decimal_precision as dp

class mrp_production(osv.osv):
    _inherit = "mrp.production"
    
    def _get_subproduction_product_qty(self, cr, uid, ids, field_names, args, context=None):
        dict = {}
        print ids
        for line in ids:
            dict[line] = 3
            return dict
    
    _columns = {
        'subproduction_ids': fields.many2many('mrp.production', 'rel_mrp_production_self', 'production_id', 'production_id2', 'Subproductions', domain=[('has_parent','=', False)]),
        'has_parent': fields.boolean('Has parent', help="If the production order has already a parent it will not be shown in subproductions."),
        #'product_subproduction_qty_real': fields.function(_get_subproduction_product_qty, type='float', method=True, string='Real used', multi=True),
        #'product_subproduction_qty_planned': fields.function(_get_subproduction_product_qty, type='float', method=True, string='Planned', multi=True),
    }

mrp_production()