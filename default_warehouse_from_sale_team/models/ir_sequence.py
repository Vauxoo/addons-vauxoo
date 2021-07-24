from odoo import fields, models


class IrSequence(models.Model):
    _inherit = "ir.sequence"

    section_id = fields.Many2one('crm.team', string='Sales Team')
