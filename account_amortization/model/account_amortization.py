# -*- encoding: utf-8 -*-
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

from openerp.osv import fields, osv


class account_asset_asset(osv.Model):

    _inherit = 'account.asset.asset'
    _description = 'Account Amortization'

    _columns = {
        'doc_type': fields.selection([('deprecation', 'Deprecation'),
            ('amortization', 'Amortization'), ], 'Type',
            help='''Asset type, deprecation allows you depreciate an asset, the
                amortization allows you amortize an expense.'''),
    }


class account_asset_category(osv.Model):

    _inherit = 'account.asset.category'
    _description = 'Account Amortization Category'

    _columns = {
        'doc_type': fields.selection([('deprecation', 'Deprecation'),
            ('amortization', 'Amortization'), ], 'Type',
            help='''Asset category type, deprecation allows you depreciate an asset, the
                amortization allows you amortize an expense.'''),
    }
