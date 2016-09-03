# -*- coding: utf-8 -*-

from openerp import fields, models


class ProcurementRule(models.Model):

    _inherit = "procurement.rule"

    propagate_transfer = fields.Boolean(
        string="Propagate transfer",
        help="When this field is check, the first stock move which is"
        " transferred triggers automatically the transfer to the other"
        " stock move related")
