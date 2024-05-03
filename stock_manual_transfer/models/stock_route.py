from odoo import fields, models


class StockRoute(models.Model):
    _inherit = "stock.route"

    manual_transfer_selectable = fields.Boolean("Applicable on manual transfer")
