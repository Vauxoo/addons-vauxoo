from odoo import api, fields, models


class IrSequence(models.Model):
    _inherit = "ir.sequence"

    section_id = fields.Many2one('crm.team', string='Sales Team')

    @api.model
    def next_by_code(self, sequence_code, sequence_date=None):
        """If a sales team is provided by context, give priority to sequences having it set"""
        if "sequence_salesteam_id" not in self.env.context:
            return super().next_by_code(sequence_code, sequence_date)
        salesteam_id = self.env.context["sequence_salesteam_id"]
        self.check_access_rights('read')
        company_id = self.env.company.id
        sequence = self.search(
            [
                ("code", "=", sequence_code),
                ("company_id", "in", [company_id, False]),
                ("section_id", "in", [salesteam_id, False]),
            ],
            limit=1,
            order="section_id, company_id"
        )
        if sequence:
            return sequence._next(sequence_date=sequence_date)
        return super().next_by_code(sequence_code, sequence_date)
