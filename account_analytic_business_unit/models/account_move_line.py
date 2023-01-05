from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    analytic_line_count = fields.Integer(compute="_compute_total_analytic_lines")
    business_unit_id = fields.Many2one(
        related="analytic_account_id.business_unit_id",
        store=True,
    )

    def action_open_analytic_lines(self):
        action = self.env["ir.actions.actions"]._for_xml_id("analytic.account_analytic_line_action_entries")
        action.update({"domain": [("id", "in", self.analytic_line_ids.ids)]})
        return action

    def _compute_total_analytic_lines(self):
        for element in self:
            element.analytic_line_count = len(element.analytic_line_ids.ids)
