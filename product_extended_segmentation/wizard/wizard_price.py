# -*- coding: utf-8 -*-
from openerp import fields, models


class WizardPrice(models.Model):
    _inherit = "wizard.price"

    update_avg_costs = fields.Boolean("Update Average Product Costs")
