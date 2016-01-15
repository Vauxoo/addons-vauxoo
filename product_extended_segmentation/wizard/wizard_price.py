from openerp import fields, models


class WizardPrice(models.TransientModel):
    _inherit = "wizard.price"

    update_avg_costs = fields.Boolean("Update Average Product Costs")
