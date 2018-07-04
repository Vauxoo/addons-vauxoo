# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
# Ch
#    Copyright (c) 2015 Vauxoo - http://www.vauxoo.com/
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

from odoo import fields, models


class WizardAssetDepreciation(models.TransientModel):
    _name = 'wizard.asset.depreciation'

    date_start = fields.Date(
        help='Select date start to depreciation lines that '
        'will write that the lines are historical', required=True)
    date_stop = fields.Date(
        help='Select date stop to depreciation lines that '
        'will write that the lines are historical', required=True)

    def write_historical_true(self):
        acc_asset_obj = self.pool.get('account.asset.asset')
        dep_line_obj = self.pool.get('account.asset.depreciation.line')
        data = self.browse(self.ids)
        date_start = data.date_start
        date_stop = data.date_stop
        for asset in acc_asset_obj.browse(data):
            asset_lines = dep_line_obj.search([
                ('asset_id', '=', asset.id),
                ('depreciation_date', '>=', date_start),
                ('depreciation_date', '<=', date_stop),
                ('move_id', '=', False)])
            for line in dep_line_obj.browse(asset_lines):
                line.write({'historical': True})
        return True
