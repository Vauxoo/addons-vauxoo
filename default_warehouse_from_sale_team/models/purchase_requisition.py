from odoo import models


class PurchaseRequisition(models.Model):
    _name = 'purchase.requisition'
    _inherit = ['purchase.requisition', 'default.picking.type.mixing']

    def _get_sequence_code(self):
        return 'purchase.order.requisition'
