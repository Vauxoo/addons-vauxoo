# coding: utf-8
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2016 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: Luis Torres <luis_t@vauxoo.com>
#    planned by: Sabrina Romero <sabrina@vauxoo.com>
############################################################################
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    @api.depends('picking_ids', 'picking_ids.state', 'state')
    def _get_allow_cancel(self):
        """If all the pickings related to a SO are on "Ready to transfer" or
        in "Waiting another move" state, the cancellation of this must be
        allowed, or even whit pickings on different states, if the moved
        product quantities are correctly returned."""
        sales = self.search([
            ('id', 'in', self.ids),
            ('state', 'in', ('manual', 'progress')),
        ])
        for sale in sales:
            if sale.picking_ids.ids:
                self._cr.execute(
                    """SELECT id FROM stock_picking
                    WHERE state not in (
                        'assigned', 'waiting', 'confirmed', 'done')
                    AND id IN %s;""", (tuple(sale.picking_ids.ids), ))
                if not self._cr.fetchall() and sale.check_prod_by_locations():
                    sale.allow_cancel = True

    @api.multi
    def _get_picking_ids(self):
        res = super(SaleOrder, self)._get_picking_ids(
            name='picking_ids', args=None)
        for sale in self:
            sale.picking_ids = res.get(sale.id)

    def _search_pickings(self, operator, value):
        pick_obj = self.env["stock.picking"]
        pick_ids = []
        if operator == 'in' and value:
            pick_ids = pick_obj.browse(value)
        elif operator and value:
            pick_ids = pick_obj.search([('name', operator, value)])
        else:
            pick_ids = pick_obj.search([])
        groups = [p.group_id.id for p in pick_ids if p.group_id]
        res = self.search([('procurement_group_id', 'in', groups)]).ids
        if operator == '=' and not value:
            return [('id', 'not in', res)]
        return [('id', 'in', res)]

    allow_cancel = fields.Boolean(
        'Allow Cancel', compute=_get_allow_cancel, store=True,
        help='This field check if all the pickings related to '
        'this SO are on "Ready to transfer", "Waiting Availability" or in '
        '"Waiting another move" or if the pickings on different states have '
        'the move of product quantities correctly returned. If this '
        'validations are True the sale order cancellation must be allowed.')
    picking_ids = fields.One2many(
        compute=_get_picking_ids, method=True, relation='stock.picking',
        string='Picking associated to this sale', search=_search_pickings)

    @api.multi
    def check_prod_by_locations(self):
        self.ensure_one()
        if not self.env['stock.picking'].search([
                ('state', '=', 'done'),
                ('id', 'in', self.picking_ids.ids)]):
            return True
        loc_src = self.warehouse_id.pick_type_id.default_location_src_id.id
        loc_dest = self.warehouse_id.pick_type_id.default_location_dest_id.id
        self.env.cr.execute(
            """
        SELECT product_id,
        array_agg(CASE WHEN (
            location_dest_id = %s) THEN product_uom_qty ELSE 0 END) AS OUT,
        array_agg(CASE WHEN (
            location_dest_id = %s) THEN product_uom_qty ELSE 0 END) AS IN
        FROM stock_move
        WHERE picking_id IN (SELECT id FROM stock_picking WHERE id in %s) and
            state='done' and location_dest_id in (%s, %s)
        GROUP BY product_id;
            """, (
            loc_src, loc_dest, tuple(self.picking_ids.ids), loc_src, loc_dest)
        )
        prods = self.env.cr.fetchall()
        for prod in prods:
            if sum(prod[1]) != sum(prod[2]):
                return False
        return True

    @api.multi
    def action_cancel_allow(self):
        for sale in self:
            if not sale.allow_cancel:
                raise ValidationError(_(
                    "To allow cancel this sale order:\n- All the pickings "
                    "are in 'Ready to transfer' or 'Waiting another move'."
                    "\n- All the moved product quantities in pickings are "
                    "correctly returned."))
        return self.action_cancel()
