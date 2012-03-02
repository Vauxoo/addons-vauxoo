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
    'cost_structure_id':fields.many2one('cost.structure','Cost Structure'),
    'cost_ult': fields.related('cost_structure_id', 'cost_ult', type='float', digits_compute=dp.get_precision('Cost Structure'), string='Last Cost'),
    'cost_prom': fields.related('cost_structure_id', 'cost_prom', type='float', digits_compute=dp.get_precision('Cost Structure'), string='Average Cost'),
    'cost_suppler': fields.related('cost_structure_id', 'cost_suppler', type='float', digits_compute=dp.get_precision('Cost Structure'), string='Supplier Cost'),
    'cost_ant': fields.related('cost_structure_id', 'cost_ant', type='float', digits_compute=dp.get_precision('Cost Structure'), string='Average Cost'),
    'ult_om': fields.related('cost_structure_id', 'ult_om', type='float', digits_compute=dp.get_precision('Cost Structure'), string='Average Cost'),
    'prom_om': fields.related('cost_structure_id', 'prom_om', type='float', digits_compute=dp.get_precision('Cost Structure'), string='Average Cost'),
    'ant_om': fields.related('cost_structure_id', 'ant_om', type='float', digits_compute=dp.get_precision('Cost Structure'), string='Average Cost'),
    'cost_to_price': fields.related('cost_structure_id', 'cost_to_price', type='selection', string='Average Cost'),
    'date': fields.related('cost_structure_id', 'date', type='date', string='Average Cost'),
    'date2': fields.related('cost_structure_id', 'date2', type='date', string='Average Cost'),
    'date3': fields.related('cost_structure_id', 'date3', type='date', string='Average Cost'),
    'date4': fields.related('cost_structure_id', 'date4', type='date', string='Average Cost'),
    'date5': fields.related('cost_structure_id', 'date5', type='date', string='Average Cost'),
    'date6': fields.related('cost_structure_id', 'date6', type='date', string='Average Cost'),
    'date7': fields.related('cost_structure_id', 'date7', type='date', string='Average Cost'),
    'date8': fields.related('cost_structure_id', 'date8', type='date', string='Average Cost'),
    'unit_price': fields.related('cost_structure_id', 'unit_price', type='float', digits_compute=dp.get_precision('Cost Structure'), string='Average Cost'),
    'unit_price2': fields.related('cost_structure_id', 'unit_price2', type='float', digits_compute=dp.get_precision('Cost Structure'), string='Average Cost'),
    'unit_price3': fields.related('cost_structure_id', 'unit_price3', type='float', digits_compute=dp.get_precision('Cost Structure'), string='Average Cost'),
    'unit_price4': fields.related('cost_structure_id', 'unit_price4', type='float', digits_compute=dp.get_precision('Cost Structure'), string='Average Cost'),
    'unit_price5': fields.related('cost_structure_id', 'unit_price5', type='float', digits_compute=dp.get_precision('Cost Structure'), string='Average Cost'),
    'date9': fields.related('cost_structure_id', 'date9', type='date', string='Average Cost'),
    'date10': fields.related('cost_structure_id', 'date10', type='date', string='Average Cost'),
    'date11': fields.related('cost_structure_id', 'date11', type='date', string='Average Cost'),
    'date12': fields.related('cost_structure_id', 'date12', type='date', string='Average Cost'),
    'date13': fields.related('cost_structure_id', 'date13', type='date', string='Average Cost'),
    'date_prom_end': fields.related('cost_structure_id', 'date_prom_end', type='date', string='Average Cost'),
    'date_prom_begin': fields.related('cost_structure_id', 'date_prom_begin', type='date', string='Average Cost'),
    'min_margin': fields.related('cost_structure_id', 'min_margin', type='float', digits_compute=dp.get_precision('Cost Structure'), string='Average Cost'),
    'margin1': fields.related('cost_structure_id', 'margin1', type='float', digits_compute=dp.get_precision('Cost Structure'), string='Average Cost'),
    'margin2': fields.related('cost_structure_id', 'margin2', type='float', digits_compute=dp.get_precision('Cost Structure'), string='Average Cost'),
    'margin3': fields.related('cost_structure_id', 'margin3', type='float', digits_compute=dp.get_precision('Cost Structure'), string='Average Cost'),
    'margin4': fields.related('cost_structure_id', 'margin4', type='float', digits_compute=dp.get_precision('Cost Structure'), string='Average Cost'),
    'margin5': fields.related('cost_structure_id', 'margin5', type='float', digits_compute=dp.get_precision('Cost Structure'), string='Average Cost'),
    'price_referen': fields.related('cost_structure_id', 'price_referen', type='float', digits_compute=dp.get_precision('Cost Structure'), string='Average Cost'),
    'price_referen2': fields.related('cost_structure_id', 'price_referen2', type='float', digits_compute=dp.get_precision('Cost Structure'), string='Average Cost'),
    'price_referen3': fields.related('cost_structure_id', 'price_referen3', type='float', digits_compute=dp.get_precision('Cost Structure'), string='Average Cost'),
    'price_referen4': fields.related('cost_structure_id', 'price_referen4', type='float', digits_compute=dp.get_precision('Cost Structure'), string='Average Cost'),
    'price_referen5': fields.related('cost_structure_id', 'price_referen5', type='float', digits_compute=dp.get_precision('Cost Structure'), string='Average Cost'),
    'margin6': fields.related('cost_structure_id', 'margin6', type='float', digits_compute=dp.get_precision('Cost Structure'), string='Average Cost'),
    'margin7': fields.related('cost_structure_id', 'margin7', type='float', digits_compute=dp.get_precision('Cost Structure'), string='Average Cost'),
    'margin8': fields.related('cost_structure_id', 'margin8', type='float', digits_compute=dp.get_precision('Cost Structure'), string='Average Cost'),
    'margin9': fields.related('cost_structure_id', 'margin9', type='float', digits_compute=dp.get_precision('Cost Structure'), string='Average Cost'),
    'margin10': fields.related('cost_structure_id', 'margin10', type='float', digits_compute=dp.get_precision('Cost Structure'), string='Average Cost'),
    'margin11': fields.related('cost_structure_id', 'margin11', type='float', digits_compute=dp.get_precision('Cost Structure'), string='Average Cost'),
    'amount': fields.related('cost_structure_id', 'amount', type='float', digits_compute=dp.get_precision('Cost Structure'), string='Amount'),
    'arancel': fields.related('cost_structure_id', 'arancel', type='float', digits_compute=dp.get_precision('Cost Structure'), string='% Arancel'),
    
    }
    
product_product()






