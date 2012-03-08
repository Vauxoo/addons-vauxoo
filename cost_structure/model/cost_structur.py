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


class cost_structure(osv.osv):
    _name = 'cost.structure'
    _columns = {
    'product_id':fields.many2one('product.product','Product',help="Product Selecet from list product"),
    'description':fields.char('Description',size=128,help="Product Description"),
    'type':fields.selection([('v', 'V'),('C', 'C')], 'Type', help="Product type"),
    'serial':fields.boolean('Serial',help="Product Serial"),
    'date_reg':fields.date('Registr Date',help="Date to registre"),
    'cost_ult':fields.float('Ult Cost',digits_compute=dp.get_precision('Cost Structure'), help="Last Cost"),
    'cost_prom':fields.float('Prom Cost',digits_compute=dp.get_precision('Cost Structure'),help="Avarage Cost"),
    'cost_suppler':fields.float('Supplier Cost',digits_compute=dp.get_precision('Cost Structure'),help="Supplier Cost"),
    'cost_ant':fields.float('Ant Cost',digits_compute=dp.get_precision('Cost Structure'),help="Last Cost"),
    'ult_om':fields.float('Ult OM',digits_compute=dp.get_precision('Cost Structure')),
    'prom_om':fields.float('Prom OM',digits_compute=dp.get_precision('Cost Structure')),
    'ant_om':fields.float('Ant OM',digits_compute=dp.get_precision('Cost Structure')),
    'date':fields.date('Date'),
    'date2':fields.date('Date'),
    'date3':fields.date('Date'),
    'date4':fields.date('Date'),
    'date5':fields.date('Date'),
    'date6':fields.date('Date'),
    'date7':fields.date('Date'),
    'date8':fields.date('Date'),
    'unit_price':fields.float('Price Unit',digits_compute=dp.get_precision('Cost Structure'),help="Price Unit"),
    'unit_price2':fields.float('Price Unit',digits_compute=dp.get_precision('Cost Structure'),help="Price Unit"),
    'unit_price3':fields.float('Price Unit',digits_compute=dp.get_precision('Cost Structure'),help="Price Unit"),
    'unit_price4':fields.float('Price Unit',digits_compute=dp.get_precision('Cost Structure'),help="Price Unit"),
    'unit_price5':fields.float('Price Unit',digits_compute=dp.get_precision('Cost Structure'),help="Price Unit"),
    'date9':fields.date('Date'),
    'date10':fields.date('Date'),
    'date11':fields.date('Date'),
    'date12':fields.date('Date'),
    'date13':fields.date('Date'),
    'date_prom_begin':fields.date('Date Prom',help="Compute Date Prom"),
    'date_prom_end':fields.date('Date End',help="Compute Date Prom with end"),
    'margin1':fields.float('Margin',digits_compute=dp.get_precision('Cost Structure'),help="Price Margin"),
    'margin2':fields.float('Margin',digits_compute=dp.get_precision('Cost Structure'),help="Price Margin"),
    'margin3':fields.float('Margin',digits_compute=dp.get_precision('Cost Structure'),help="Price Margin"),
    'margin4':fields.float('Margin',digits_compute=dp.get_precision('Cost Structure'),help="Price Margin"),
    'margin5':fields.float('Margin',digits_compute=dp.get_precision('Cost Structure'),help="Price Margin"),
    'min_margin':fields.float('% Margin',digits_compute=dp.get_precision('Cost Structure'),help="Porcent Margin Min"),
    'price_referen':fields.float('Price Reference',digits_compute=dp.get_precision('Cost Structure'),help="Price Reference"),
    'price_referen2':fields.float('Price Reference',digits_compute=dp.get_precision('Cost Structure'),help="Price Reference"),
    'price_referen3':fields.float('Price Reference',digits_compute=dp.get_precision('Cost Structure'),help="Price Reference"),
    'price_referen4':fields.float('Price Reference',digits_compute=dp.get_precision('Cost Structure'),help="Price Reference"),
    'price_referen5':fields.float('Price Reference',digits_compute=dp.get_precision('Cost Structure'),help="Price Reference"),
    'margin6':fields.float('Margin',digits_compute=dp.get_precision('Cost Structure'),help="Price Margin"),
    'margin7:fields.float('Margin',digits_compute=dp.get_precision('Cost Structure'),help="Price Margin"),
    'margin8':fields.float('Margin',digits_compute=dp.get_precision('Cost Structure'),help="Price Margin"),
    'margin9':fields.float('Margin',digits_compute=dp.get_precision('Cost Structure'),help="Price Margin"),
    'margin10':fields.float('Margin',digits_compute=dp.get_precision('Cost Structure'),help="Price Margin"),
    'amount':fields.float('Amount',digits_compute=dp.get_precision('Cost Structure'),help="Amount"),
    'arancel':fields.float('% Arancel',digits_compute=dp.get_precision('Cost Structure'),help="Porcent Arancel"),
    }
    
    _rec_name = 'product_id'
    
cost_structure()
