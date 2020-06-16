from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class AccountAssetDepreciationLine(models.Model):
    _inherit = 'account.asset.depreciation.line'

    @api.depends('move_id')
    def _compute_move_check(self):
        for line in self:
            line.move_check = bool(line.move_id or line.historical)

        return super()._compute_move_check()

    historical = fields.Boolean(help="Check box for the historical validation",
                                default=False)
    move_check = fields.Boolean(help="Compute the move status",
                                compute="_compute_move_check",
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
