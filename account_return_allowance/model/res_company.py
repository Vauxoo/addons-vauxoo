# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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



class res_company(osv.Model):
    """
    OpenERP Model : res_company
    """

    _inherit = 'res.company'

    _columns = {
        'make_allowance_aml': fields.boolean('Make Allowance Move Line',
                                             required=False,
        help="""With this in true every sale invoice will make an extra move line
        carrying the amount of the discount to allowance account configured
        on product or categ_product or company in this order."""),
        'property_account_allowance_global': fields.property(
            'account.account',
            type='many2one',
            relation='account.account',
            string="Invoice allowance global account",
            method=True,
            view_load=True,
            domain="[('type', '=', 'other')]",
            help="""This Account is used to make move line for globals discounts
            on sale invoices and represent this amount as a counter part on debit
            for an income."""),
        'make_return_aml': fields.boolean('Make Return on Separate Account',
                                          required=False,
        help="""True, the refund for Sale Invoice will be expresed on this account
         or in the account defined on product or category of product, allowing
         credit returns in a different account complying with accounting global standars.."""),
        'property_account_return_global': fields.property(
            'account.account',
            type='many2one',
            relation='account.account',
            string="Invoice allowance global account",
            method=True,
            view_load=True,
            domain="[('type', '=', 'other')]",
            help="""This Account is used to make move line for globals return
            on out invoices and represent this amount as a counter part on credit
            for an income."""),
    }
