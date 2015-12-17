# -*- coding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Sabrina Romero (sabrina@vauxoo.com)
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

from openerp import models, fields


class AccountAssetAsset(models.Model):

    _inherit = 'account.asset.asset'
    _description = 'Account Amortization'

    doc_type = fields.Selection(
        selection=[
            ('depreciation', 'Depreciation'),
            ('amortization', 'Amortization')], string='Type',
        default='depreciation', help='''Asset type,
        depreciation allows you depreciate an asset, the amortization
        allows you amortize an expense.''')


class AccountAssetCategory(models.Model):

    _inherit = 'account.asset.category'
    _description = 'Account Amortization Category'

    doc_type = fields.Selection([('depreciation', 'Depreciation'),
                                ('amortization', 'Amortization'), ], 'Type',
                                default='depreciation',
                                help='''Asset category type, depreciation
                                allows you depreciate an asset, the
                                amortization allows you amortize
                                an expense.''')
