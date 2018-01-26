# -*- coding: utf-8 -*-
###########################################################################
#    Module Writen to Odoo, Open Source Management Solution
#
#    Copyright (c) 2018 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
#    Coded by: Edgar Rivero (edgar@vauxoo.com)
############################################################################
from odoo import api, fields, models


class ChangeRouteProduction(models.TransientModel):
    _name = 'change.route.production'
    _description = 'Change Route Production'

    production_id = fields.Many2one(
        'mrp.production', readonly=True,
        default=lambda self: self.env.context.get('active_id', False))
    product_tmpl_id = fields.Many2one(
        'product.template',
        related='production_id.product_id.product_tmpl_id', readonly=True)
    bom_id = fields.Many2one(
        'mrp.bom', string='Materials list', required=True,
        domain="[('product_id', '=', product_id)]")
    routing_id = fields.Many2one(
        'mrp.routing', string='Production route', related='bom_id.routing_id',
        readonly=True)

    @api.multi
    def change_route(self):
        """ This function changes the route of the production order,
        creating a new production order and canceling the current order
        """
        self.ensure_one()
        context = dict(self.env.context or {})
        id = self.env.context.get('active_id', False)
        return True
