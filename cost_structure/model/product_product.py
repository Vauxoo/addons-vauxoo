#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Vauxoo C.A.           
#    Planified by: Nhomar Hernandez
#    Audited by: Vauxoo C.A.
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
################################################################################

from osv import fields, osv
import tools
from tools.translate import _
from tools import config
import netsvc
import decimal_precision as dp


class product_product(osv.osv):
    
    _inherit = 'product.product'
    _columns = {
    'property_cost_structure': fields.property(
    'cost.structure',
    type='many2one',
    relation='cost.structure',
    string="Cost and Price Structure",
    method=True,
    view_load=True,
    help="For the current product, this cost and price strucuture will define how the behavior of the price and cost computation "),
    'cost_ult': fields.related('property_cost_structure', 'cost_ult', type='float', digits_compute=dp.get_precision('Cost Structure'), string='Last Cost'),
    'cost_prom': fields.related('property_cost_structure', 'cost_prom', type='float', digits_compute=dp.get_precision('Cost Structure'), string='Average Cost'),
    'cost_suppler': fields.related('property_cost_structure', 'cost_suppler', type='float', digits_compute=dp.get_precision('Cost Structure'), string='Supplier Cost'),
    'cost_ant': fields.related('property_cost_structure', 'cost_ant', type='float', digits_compute=dp.get_precision('Cost Structure'), string='Ant Cost'),
    'ult_om': fields.related('property_cost_structure', 'ult_om', type='float', digits_compute=dp.get_precision('Cost Structure'), string='Ult Cost'),
    'prom_om': fields.related('property_cost_structure', 'prom_om', type='float', digits_compute=dp.get_precision('Cost Structure'), string='UOM Prom'),
    'ant_om': fields.related('property_cost_structure', 'ant_om', type='float', digits_compute=dp.get_precision('Cost Structure'), string='UOM Ant'),
    'cost_to_price': fields.related('property_cost_structure', 'cost_to_price', type='selection', string='Average Cost'),
    'date_cost_ult': fields.related('property_cost_structure', 'date_cost_ult', type='date', string='Date'),
    'date_ult_om': fields.related('property_cost_structure', 'date_ult_om', type='date', string='Date'),
    'date_cost_prom': fields.related('property_cost_structure', 'date_cost_prom', type='date', string='Date'),
    'date_prom_om': fields.related('property_cost_structure', 'date_prom_om', type='date', string='Date'),
    'date_cost_suppler': fields.related('property_cost_structure', 'date_cost_suppler', type='date', string='Date'),
    'date_ant_om': fields.related('property_cost_structure', 'date_ant_om', type='date', string='Date'),
    'date_cost_ant': fields.related('property_cost_structure', 'date_cost_ant', type='date', string='Date'),
    'date_cost_to_price': fields.related('property_cost_structure', 'date_cost_to_price', type='date', string='Date'),
    'method_cost_ids': fields.related('property_cost_structure', 'method_cost_ids', relation='method.price', type='one2many', string='Method Cost'),
    
    }
    
product_product()






