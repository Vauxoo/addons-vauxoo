from odoo import models


class PurchaseRequisition(models.Model):
    _name = 'purchase.requisition'
    _inherit = ['purchase.requisition', 'default.picking.type.mixing']

    def action_in_progress(self):
        """Pass team by context so sequence number is computed

        Since requisition name is not assigned when it's created but when confirmed,
        we need to pass the sales team by context also here.
        """
        self_team = self.with_context(sequence_salesteam_id=self.warehouse_id.sale_team_ids[:1].id)
        return super(PurchaseRequisition, self_team).action_in_progress()
