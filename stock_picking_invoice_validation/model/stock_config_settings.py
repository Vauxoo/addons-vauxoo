# coding: utf-8
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: hugo@vauxoo.com
#    planned by: Nhomar Hernandez <nhomar@vauxoo.com>
############################################################################
from openerp import api, fields, models


class StockConfigSettings(models.TransientModel):
    _inherit = 'stock.config.settings'

    # general validation to check picking vs invoice
    check_inv_pick = fields.Boolean("Check invoice vs picking")

    @api.model
    def get_default_check_inv_pick(self, fields_name):
        key = "stock.check_inv_pick"
        check_inv_pick = self.env["ir.config_parameter"].get_param(
            key, default=True)
        return {'check_inv_pick': check_inv_pick}

    @api.multi
    def set_default_check_inv_pick(self):
        config_parameters = self.env["ir.config_parameter"]
        key = "stock.check_inv_pick"
        config_parameters.set_param(
            key, self.check_inv_pick or True, [])
