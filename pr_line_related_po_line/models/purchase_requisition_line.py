from odoo import fields, models


class PurchaseRequisitionLine(models.Model):
    _inherit = 'purchase.requisition.line'

    purchase_order_line_ids = fields.One2many(
        'purchase.order.line', 'purchase_requisition_line_id',
        string="Purchase Order Lines")

    def _prepare_purchase_order_line(self, name, product_qty=0.0, price_unit=0.0, taxes_ids=False):
        """Inherit method to add the relation between the purchase order line that is being created from the
        requisition and the purchase requisition line.
        """
        res = super()._prepare_purchase_order_line(name, product_qty, price_unit, taxes_ids)
        res['purchase_requisition_line_id'] = self.id
        return res
