# coding: utf-8

from odoo import models, api, fields


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    state = fields.Selection(selection_add=[
        ('third approve', 'Third Approve')])

    @api.multi
    def button_approve(self, force=False):
        group = 'purchase_third_validation.general_purchase_manager'
        limit = self.env.user.company_id.currency_id.compute(
            self.company_id.po_third_validation_amount, self.currency_id)
        if self.company_id.po_double_validation in ['one_Step', 'two_step']\
                or (self.company_id.po_double_validation == 'three_step'
                    and self.amount_total < limit)\
                or self.user_has_groups(group):
            return super(PurchaseOrder, self).button_approve(force)
        self.write({'state': 'third approve'})
        return {}
