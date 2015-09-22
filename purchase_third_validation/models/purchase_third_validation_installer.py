# coding: utf-8
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2015 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: aguzman@vauxoo.com
#              Luis Torres <luis_t@vauxoo.com>
#    planned by: Sabrina Romero <sabrina@vauxoo.com>
############################################################################

from openerp import models, fields, api
from openerp import exceptions


class PurchaseConfigSettings(models.TransientModel):
    _inherit = 'purchase.config.settings'

    limit_amount_t = fields.Integer(
        'Limit to require the approbation of a third user',
        required=True,
        help="Amount after which a third validation of purchase is required.")

    @api.model
    def get_default_limit_amount(self, fields_f):
        res = super(PurchaseConfigSettings, self).get_default_limit_amount(
            fields_f)
        ir_model_data = self.env['ir.model.data']
        transition = ir_model_data.get_object(
            'purchase_third_validation',
            'trans_less_third')
        value = transition.condition.split('<', 1)
        res.update({'limit_amount_t': int(value[1])})
        return res

    @api.one
    def set_limit_amount(self):
        super(PurchaseConfigSettings, self).set_limit_amount()
        ir_model_data = self.env['ir.model.data']
        waiting = ir_model_data.get_object(
            'purchase_third_validation',
            'trans_less_third')
        waiting.write(
            {'condition': 'amount_total < %s' % (self.limit_amount_t)})

    @api.one
    @api.constrains(
        'limit_amount_t', 'limit_amount', 'module_purchase_double_validation')
    def _check_amount_validations(self):
        if self.module_purchase_double_validation and\
                (self.limit_amount > self.limit_amount_t):
            raise exceptions.Warning(
                'The limit amount to the second approbation must be less that '
                'amount to third validation')
