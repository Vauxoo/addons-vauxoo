# coding: utf-8

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import Warning as WarningUser


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    po_order_approval = fields.Boolean(
        "Order Approval",
        default=lambda self: self.env.user.company_id.po_double_validation in
        ['two_step', 'three_step'])
    po_third_order_approval = fields.Boolean(
        "Third Order Approval",
        default=lambda self: self.env.user.company_id.po_double_validation
        == 'three_step')
    po_third_validation_amount = fields.Monetary(
        related='company_id.po_third_validation_amount',
        string="Third Validation Minimum Amount", currency_field='company_currency_id', readonly=False)

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.po_double_validation = 'three_step' if self.\
            po_third_order_approval else 'two_step' if self.\
            po_order_approval else 'one_step'
        return res

    @api.multi
    @api.constrains(
        'po_third_validation_amount', 'po_double_validation_amount')
    def _check_amount_validations(self):
        if self.po_double_validation_amount > self.po_third_validation_amount:
            raise WarningUser(_(
                'The limit amount to the second approbation must be less than\
                the amount to third validation.'))
