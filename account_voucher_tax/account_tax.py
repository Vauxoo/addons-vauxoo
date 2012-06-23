# -*- coding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: Rodo (rodo@vauxoo.com),Moy (moylop260@vauxoo.com)
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
from osv import osv, fields

#TODO List:
#   *Hay que modificar la venta, para que tome en el descripción el product_code & product_name del cliente, en su pedido de venta.
#   *index to product_code
#   *Agregar contraint (analizando todas las variantes)
#   *Hacerlo multi-company (company_id & defaults)
#   *Agregar su security.csv

class account_tax(osv.osv):
     _inherit = "account.tax"
     
     _columns = {
          'tax_voucher_ok': fields.boolean('Tax Vocuher Ok',help='help'),
          'account_collected_voucher_id': fields.many2one('account.account','Account Collected Voucher'),
          'account_paid_voucher_id': fields.many2one('account.account','Account Paid Voucher'),
     }
     
account_tax()