from odoo import fields, models


class StockLocationRoute(models.Model):
    _inherit = "stock.location.route"

    manual_transfer_selectable = fields.Boolean("Applicable on manual transfer")
