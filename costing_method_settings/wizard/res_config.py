# coding: utf-8
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
###############################################################################
#    Credits:
#    Coded by: Katherine Zaoral <kathy@vauxoo.com>
#    Planified by: Katherine Zaoral <kathy@vauxoo.com>
#    Audited by: Katherine Zaoral <kathy@vauxoo.com>
###############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################

from openerp import models, fields, api


class PurchaseConfigSettings(models.TransientModel):

    _inherit = 'purchase.config.settings'

    default_cost_method = fields.Selection(
        selection=[
            ('standard', 'Standard Price'), ('average', 'Average Price'),
            ('real', 'Real Price')],
        string="Default Product Costing Method",
        default_model="product.template",
        help="Set the Product default costing method"
    )

    @api.onchange('default_cost_method')
    def active_group_costing_method(self):
        """Set the group_costing_method to true when the default_cost_method is
        set
        """
        if self.default_cost_method:
            self.group_costing_method = True
