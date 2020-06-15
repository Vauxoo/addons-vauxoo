# -*- coding: utf-8 -*-
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: Katherine Zaoral <kathy@vauxoo.com>
#    planned by: Nhomar Hernandez <nhomar@vauxoo.com>
############################################################################

from odoo import fields, models, api, _
from odoo.tools.float_utils import float_compare, float_is_zero
from odoo.exceptions import UserError


class StockMove(models.Model):

    _inherit = 'stock.move'

    # pylint: disable=too-complex
    # pylint: disable=except-pass
    @api.multi
    def has_validate_picking_after_move_date(self):
        """ Check if there are pickings for the same product that have already
        quants in a date future that the one in the move
        """
        quant_obj = self.env['stock.quant']
        quants = quant_obj.search([
            ('product_id', '=', self.product_id.id),
            ('in_date', '>', self.date),
        ], limit=1)
        return bool(quants)

    def _action_done(self):
        """NOTE: This method is a copy of the original one in odoo named action_done but we add
        a new section of code to introduce exception on the test.

        Look for "# NOTE VX: This section was overwritten." to find the added code.
        """
        if not self._context.get('allow_past_date_quants'):
            return super(StockMove, self)._action_done()

        self.filtered(lambda move: move.state == 'draft')._action_confirm()  # MRP allows scrapping draft moves
        moves = self.exists().filtered(lambda x: x.state not in ('done', 'cancel'))
        moves_todo = self.env['stock.move']

        # Cancel moves where necessary ; we should do it before creating the extra moves because
        # this operation could trigger a merge of moves.
        for move in moves:
            if move.quantity_done <= 0:
                if float_compare(move.product_uom_qty, 0.0, precision_rounding=move.product_uom.rounding) == 0:
                    move._action_cancel()

        # Create extra moves where necessary
        for move in moves:
            if move.state == 'cancel' or move.quantity_done <= 0:
                continue

            moves_todo |= move._create_extra_move()

        # Split moves where necessary and move quants
        for move in moves_todo:
            # To know whether we need to create a backorder or not, round to the general product's
            # decimal precision and not the product's UOM.
            rounding = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            if float_compare(move.quantity_done, move.product_uom_qty, precision_digits=rounding) < 0:
                # Need to do some kind of conversion here
                qty_split = move.product_uom._compute_quantity(
                    move.product_uom_qty - move.quantity_done, move.product_id.uom_id, rounding_method='HALF-UP')
                new_move = move._split(qty_split)
                for move_line in move.move_line_ids:
                    if move_line.product_qty and move_line.qty_done:
                        # FIXME: there will be an issue if the move was partially available
                        # By decreasing `product_qty`, we free the reservation.
                        # FIXME: if qty_done > product_qty, this could raise if nothing is in stock
                        try:
                            move_line.write({'product_uom_qty': move_line.qty_done})
                        except UserError:
                            pass
                move._unreserve_initial_demand(new_move)
        moves_todo.mapped('move_line_ids')._action_done()
        # Check the consistency of the result packages; there should be an unique location across
        # the contained quants.
        for result_package in moves_todo\
                .mapped('move_line_ids.result_package_id')\
                .filtered(lambda p: p.quant_ids and len(p.quant_ids) > 1):
            if len(result_package.quant_ids.filtered(lambda q: not float_is_zero(abs(q.quantity) + abs(
                    q.reserved_quantity), precision_rounding=q.product_uom_id.rounding)).mapped('location_id')) > 1:
                raise UserError(_('You cannot move the same package content more than once in the same transfer '
                                  'or split the same package into two location.'))
        picking = moves_todo.mapped('picking_id')

        # NOTE VX: This section was overwritten.
        date_now = fields.Datetime.now()
        for move in moves_todo:
            move_date = move.has_validate_picking_after_move_date() and date_now or move.date
            move.write({'state': 'done', 'date': move_date})
        # NOTE VX: End of overwrite

        moves_todo.mapped('move_dest_ids')._action_assign()

        # We don't want to create back order for scrap moves
        # Replace by a kwarg in master
        if self.env.context.get('is_scrap'):
            return moves_todo

        if picking:
            picking._create_backorder()
        for move in moves_todo:
            # Apply restrictions on the stock move to be able to make
            # consistent accounting entries.
            if move._is_in() and move._is_out():
                raise UserError(_("The move lines are not in a consistent state: "
                                  "some are entering and other are leaving the company."))
            company_src = move.mapped('move_line_ids.location_id.company_id')
            company_dst = move.mapped('move_line_ids.location_dest_id.company_id')
            try:
                if company_src:
                    company_src.ensure_one()
                if company_dst:
                    company_dst.ensure_one()
            except ValueError:
                raise UserError(_("The move lines are not in a consistent states: "
                                  "they do not share the same origin or destination company."))
            if company_src and company_dst and company_src.id != company_dst.id:
                raise UserError(_("The move lines are not in a consistent states: they are doing an intercompany "
                                  "in a single step while they should go through the intercompany transit location."))
            move._run_valuation()
        for move in moves_todo.filtered(lambda m: m.product_id.valuation == 'real_time' and (
                m._is_in() or m._is_out() or m._is_dropshipped() or m._is_dropshipped_returned())):
            move._account_entry_move()
        return moves_todo
