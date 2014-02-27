# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: julio (julio@vauxoo.com)
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
from openerp.osv import osv, fields


class stock_location(osv.Model):
    _inherit = 'stock.location'

    _columns = {
        'variation_in_account_id': fields.many2one('account.account',
            'Stock Variation Account (Incoming)',
            domain=[('type', '=', 'other')]),
        'variation_out_account_id': fields.many2one('account.account',
            'Stock Variation Account (Outgoing)',
            domain=[('type', '=', 'other')]),
        'property_account_in_production_price_difference': fields.property(
            'account.account',
            type='many2one',
            relation='account.account',
            string='Price Production Variation Account (Incoming)',
            view_load=True,
            domain=[('type', '=', 'other')]),
        'property_account_out_production_price_difference': fields.property(
            'account.account',
            type='many2one',
            relation='account.account',
            string='Price Production Variation Account (Outgoing)',
            view_load=True,
            domain=[('type', '=', 'other')]),
    }
