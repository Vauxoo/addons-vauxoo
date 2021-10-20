from odoo import models


class PurchaseOrder(models.Model):
    _name = 'purchase.order'
    _inherit = ["default.picking.type.mixing", "purchase.order"]
