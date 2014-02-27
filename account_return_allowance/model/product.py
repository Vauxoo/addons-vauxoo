# -*- encoding: utf-8 -*-
##############################################################################
#
#    VAUXOO, C.A.
#    Copyright (C) VAUXOO, C.A. (<http://www.vauxoo.com>). All Rights Reserved
#    hbto@vauxoo.com
# Credits######################################################
#    Coded by: Vauxoo C.A.
#    Planified by: Nhomar Hernandez
#    Audited by: Vauxoo C.A.
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import fields, osv
from openerp.tools.translate import _

from tools import config

from datetime import datetime


class product_category(osv.Model):
    _inherit = 'product.category'
    _columns = {
        'property_account_allowance': fields.property(
            'account.account',
            type='many2one',
            relation='account.account',
            string="Allowance Account",
            method=True,
            view_load=True,
            help="Discount on the balance of the product This account will be 
            used to book Allowances when making Customer Refunds. 
            Allowance: refer to reductions in price to due to minor defect"),
        'property_account_return': fields.property(
            'account.account',
            type='many2one',
            relation='account.account',
            string="Sale Return Account",
            method=True,
            view_load=True,
            help="Comercial credit note, This account will be used to book 
            Sale Returns when making Customer Refunds."),
    }



class product_template(osv.Model):
    _inherit = 'product.template'
    _columns = {
        'property_account_allowance': fields.property(
            'account.account',
            type='many2one',
            relation='account.account',
            string="Allowance Account",
            method=True,
            view_load=True,
            help="Discount on the balance of the product This account will be used to book Allowances when making Customer Refunds."),
        'property_account_return': fields.property(
            'account.account',
            type='many2one',
            relation='account.account',
            string="Sale Return Account",
            method=True,
            view_load=True,
            help="Comercial credit note,This account will be used to book Sale Returns when making Customer Refunds."),
    }

