# -*- coding: utf-8 -*-
###########################################################################
#    Module Writen to Odoo, Open Source Management Solution
#
#    Copyright (c) 2018 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
#    Coded by: Edgar Rivero (edgar@vauxoo.com)
############################################################################
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, DEFAULT_SERVER_DATETIME_FORMAT


class ChangeRouteProduction(models.TransientModel):
    _name = 'change.route.production'
    _description = 'Change Route Production'

    production_id = fields.Many2one(
        'mrp.production', readonly=True,
        default=lambda self: self.env.context.get('active_id', False))
    product_tmpl_id = fields.Many2one(
        'product.template',
        related='production_id.product_id.product_tmpl_id', readonly=True)
    bom_current_id = fields.Many2one(
        'mrp.bom', string='Materials list current',
        related='production_id.bom_id', readonly=True)
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
        if self.production_id.state in ['cancel', 'done']:
            raise UserError(_('Production orders in canceled or done state '
                              'can not be changed production routes.'))

        prod = self._action_procurement_create(self.production_id)
        if prod:
            prod.backorder_id = self.production_id
            self.production_id.write(
                {'procurement_ids': [(4, prod.procurement_ids.id)]})
            self.production_id.action_cancel()
            return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'mrp.production',
                'type': 'ir.actions.act_window',
                'res_id': prod.id,
                'context': self.env.context
            }
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def _prepare_line_procurement(self, production, quantity, group_id=False):
        self.ensure_one()
        return {
            'name': production.name,
            'origin': production.name,
            'date_planned': datetime.strptime(
                production.date_planned_finished,
                DEFAULT_SERVER_DATETIME_FORMAT),
            'product_id': production.product_id.id,
            'product_qty': quantity,
            'product_uom': production.product_uom_id.id,
            'location_id': production.location_dest_id.id,
            'company_id': production.company_id.id,
            'group_id': group_id,
            'bom_id': self.bom_id.id
        }

    @api.multi
    def _action_procurement_create(self, production):
        """Create procurement based on quantity. If the quantity is
        greater than 0, a new procurement is created.
        """
        self.ensure_one()
        precision = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        proc_obj = self.env['procurement.order']
        rule_obj = self.env['procurement.rule']
        prod_obj = self.env['mrp.production']
        qty = production.product_qty - production.qty_produced

        if float_is_zero(qty, precision_digits=precision):
            raise UserError(_('There is nothing left to produce'))
        if not production.procurement_group_id:
            vals = {'name', production.name}
            production.procurement_group_id = proc_obj.create(vals)

        vals = self._prepare_line_procurement(
            production, qty, group_id=production.procurement_group_id.id)

        if production.procurement_ids:
            procurement = production.procurement_ids[0]
            vals['rule_id'] = procurement.rule_id.id
            vals['orderpoint_id'] = procurement.orderpoint_id.id
            vals['warehouse_id'] = procurement.orderpoint_id.id

        else:
            vals['rule_id'] = rule_obj.search(
                [('action', '=', 'manufacture')], limit=1).id

        new_proc = proc_obj.with_context(
            procurement_autorun_defer=True).create(vals)
        new_proc.message_post_with_view(
            'mail.message_origin_link',
            values={'self': new_proc, 'origin': production},
            subtype_id=self.env.ref('mail.mt_note').id)
        new_prod = new_proc.make_mo()
        prod = prod_obj.browse(new_prod.get(new_proc.id, []))
        new_proc.write({'state': 'running', 'production_id': prod.id})
        return prod
