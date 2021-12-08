from odoo import fields, models


class PurchaseOrderLine(models.Model):

    _inherit = 'purchase.order.line'

    purchase_requisition_line_id = fields.Many2one(
        'purchase.requisition.line')
