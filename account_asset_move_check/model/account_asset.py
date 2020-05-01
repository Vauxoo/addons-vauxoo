# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
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

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class AccountAssetDepreciationLine(models.Model):
    _inherit = 'account.asset.depreciation.line'

    @api.depends('move_id')
    def _get_move_check(self):
        for line in self:
            line.move_check = bool(line.move_id or line.historical)

        return super(AccountAssetDepreciationLine, self)._get_move_check()

    historical = fields.Boolean(help="Check box for the historical validation",
                                default=False)
    move_check = fields.Boolean(help="Compute the move status",
                                compute="_get_move_check",
                                string='Move Posted', store=True)


class AccountAssetAsset(models.Model):
    _inherit = 'account.asset.asset'

    value_residual = fields.Float(
        help="Stores the value of the process",
        digits=dp.get_precision('Account'), compute="_amount_residual",
        string='Net Book Value')

    def _amount_residual(self):
        dep_line_obj = self.env['account.asset.depreciation.line']
        for asset in self:
            dep_lines = dep_line_obj.search(
                [('asset_id', '=', asset.id),
                    ('move_id', '=', False),
                    ('move_check', '=', True)])
            amount = 0
            for line in dep_lines:
                amount += line.amount or 0.0
            asset.value_residual = amount
        return super(AccountAssetAsset, self)._amount_residual()
