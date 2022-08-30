from odoo import api, fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    business_unit_id = fields.Many2one(
        "account.analytic.business.unit",
        compute="_compute_business_unit_id",
        inverse="_inverse_business_unit_id",
        readonly=False,
        store=True,
    )

    @api.depends("account_id", "account_id.business_unit_id")
    def _compute_business_unit_id(self):
        for element in self:
            element.business_unit_id = element.account_id.business_unit_id

    def _inverse_business_unit_id(self):
        pass
