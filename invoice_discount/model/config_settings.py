# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2014 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Luis Torres (luis_t@vauxoo.com)
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
'''
File to add functionalitity in account.invoice.line to get the amount without
discount and the value of the discount
'''
from openerp.osv import osv


class SaleConfigSettings(osv.TransientModel):
    _inherit = 'sale.config.settings'

    def get_default_sale_config_settings(self, cr, uid, fields, context=None):
        return {'group_discount_per_so_line': True}

    def action_sale_config_settings(self, cr, uid, context=None):
        res = self.create(cr, uid, {'group_discount_per_so_line': True},
                          context=context)
        self.execute(cr, uid, [res], context=context)
        return True
