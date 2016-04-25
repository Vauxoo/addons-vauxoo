# coding: utf-8
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
###############################################################################
#    Credits:
#    Coded by: Yanina Aular <yani@vauxoo.com>
#    Planified by: Gabriela Quilarque <gabriela@vauxoo.com>
#    Audited by: Nhomar Hernandez <nhomar@vauxoo.com>
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

from openerp import api, models


class StockConfigSettings(models.TransientModel):
    """Add method to configure the stock config settings.
    """
    _inherit = "stock.config.settings"

    @api.model
    def action_stock_config_settings_lot_repeated(self):
        """Active tracks lots or serial numbers
        @return True
        """
        res = self.create({
            "group_stock_production_lot": True,
            "company_id": self.env.ref("base.main_company").id
        })
        res.execute()
        return True
