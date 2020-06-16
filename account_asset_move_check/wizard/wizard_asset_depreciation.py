from odoo import fields, models


class WizardAssetDepreciation(models.TransientModel):
    _name = 'wizard.asset.depreciation'
    _description = 'wizard.asset.depreciation'

    date_start = fields.Date(
        help='Select date start to depreciation lines that '
        'will write that the lines are historical', required=True)
    date_stop = fields.Date(
        help='Select date stop to depreciation lines that '
        'will write that the lines are historical', required=True)

    def write_historical_true(self):
        date_start = self.date_start
        date_stop = self.date_stop
        for asset in self.env.context['active_ids']:
            asset_lines = self.env['account.asset.depreciation.line'].search([
                ('asset_id', '=', asset),
                ('depreciation_date', '>=', date_start),
                ('depreciation_date', '<=', date_stop),
                ('move_id', '=', False)])
            asset_lines.write({'historical': True})
        return True
