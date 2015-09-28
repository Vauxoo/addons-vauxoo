# coding: utf-8
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2015 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: Luis Torres <luis_t@vauxoo.com>
############################################################################

from openerp import models, api, fields, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def _check_level(self):
        ir_model_data = self.env['ir.model.data']
        transition = ir_model_data.get_object(
            'purchase_third_validation',
            'trans_less_third')
        value = transition.condition.split('<', 1)
        for purchase in self:
            if purchase.state == 'confirmed' and\
                    purchase.currency_id.compute(
                        purchase.amount_total,
                        purchase.company_id.currency_id) >= float(value[1]):
                purchase.third_level_ok = True

    third_level_ok = fields.Boolean(
        compute=_check_level, string='Third level',
        help='If the PO exceeds the amount set to need a third level of '
        'validation, this value is True', store=False)

    @api.model
    def send_dummy_mesage(self):
        self.message_post(
            body=_('The PO was not approved, you need privileges by the amount'
                   ' of this purchase'))
        return False

    @api.multi
    def amount_currency_company(self, amount_purchase):
        amount_currency = self.currency_id.compute(
            amount_purchase, self.company_id.currency_id)
        return amount_currency
