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

import time
from datetime import datetime

from openerp import models, api, _
from odoo.exceptions import UserError
from openerp.tools.float_utils import float_compare, float_round
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class StockMove(models.Model):

    _inherit = 'stock.move'

    @api.multi
    def has_validate_picking_after_move_date(self):
        """ Check if there are pickings for the same product that have already
        quants in a date future that the one in the move
        """
        quant_obj = self.env['stock.quant']
        quants = quant_obj.search([
            ('product_id', '=', self.product_id.id),
            ('in_date', '>', self.date),
        ])
        return bool(quants)

    @api.multi
    def action_done(self):
        if self._context.get('allow_past_date_quants', False):
            res = self.action_done_allow_past_date()
        else:
            res = super(StockMove, self).action_done()
        return res

    @api.multi
    def action_done_allow_past_date(self):
        """NOTE: This method is a copy of the original one in odoo named
        action_done but we add a new sectiond of conde to introduce exception
        on the test.

        Look for "# NOTE VX: This section was overwritten." to find the added
        code.
        """
        self.filtered(lambda move: move.state == 'draft').action_confirm()

        Quant = self.env['stock.quant']

        pickings = self.env['stock.picking']
        procurements = self.env['procurement.order']
        operations = self.env['stock.pack.operation']

        remaining_move_qty = {}

        for move in self:
            if move.picking_id:
                pickings |= move.picking_id
            remaining_move_qty[move.id] = move.product_qty
            for link in move.linked_move_operation_ids:
                operations |= link.operation_id
                pickings |= link.operation_id.picking_id

        # Sort operations according to entire packages first, then package +
        # lot, package only, lot only
        operations = operations.sorted(
            key=lambda x: (
                (x.package_id and not x.product_id) and -4 or 0) +
            (x.package_id and -2 or 0) + (x.pack_lot_ids and -1 or 0))

        for operation in operations:

            # product given: result put immediately in the result package (if
            # False: without package)
            # but if pack moved entirely, quants should not be written anything
            # for the destination package
            quant_dest_package_id = (
                operation.result_package_id.id if operation.product_id
                else False)
            entire_pack = not operation.product_id and True or False

            # compute quantities for each lot + check quantities match
            lot_quantities = dict(
                (pack_lot.lot_id.id,
                 operation.product_uom_id._compute_quantity(
                     pack_lot.qty, operation.product_id.uom_id)
                 ) for pack_lot in operation.pack_lot_ids)

            qty = operation.product_qty
            if (operation.product_uom_id and
                    operation.product_uom_id != operation.product_id.uom_id):
                qty = operation.product_uom_id._compute_quantity(
                    qty, operation.product_id.uom_id)
            if operation.pack_lot_ids and float_compare(
                sum(lot_quantities.values()), qty,
                    precision_rounding=operation.product_id.
                    uom_id.rounding) != 0.0:
                raise UserError(
                    _('You have a difference between the quantity '
                      'on the operation and the quantities specified '
                      'for the lots. '))

            quants_taken = []
            false_quants = []
            lot_move_qty = {}

            prout_move_qty = {}
            for link in operation.linked_move_operation_ids:
                prout_move_qty[link.move_id] = prout_move_qty.get(
                    link.move_id, 0.0) + link.qty

            # Process every move only once for every pack operation
            for move in prout_move_qty.keys():
                # TDE FIXME: do in batch ?
                move.check_tracking(operation)

                # TDE FIXME: I bet the message error is wrong
                if not remaining_move_qty.get(move.id):
                    raise UserError(
                        _("The roundings of your unit of measure %s "
                          "on the move vs. %s on the product don't allow "
                          "to do these operations or you are not transferring "
                          "the picking at once. ") %
                        (move.product_uom.name, move.product_id.uom_id.name))

                if not operation.pack_lot_ids:
                    preferred_domain_list = [
                        [('reservation_id', '=', move.id)],
                        [('reservation_id', '=', False)],
                        ['&', ('reservation_id', '!=', move.id),
                         ('reservation_id', '!=', False)]]
                    quants = Quant.quants_get_preferred_domain(
                        prout_move_qty[move], move,
                        ops=operation, domain=[('qty', '>', 0)],
                        preferred_domain_list=preferred_domain_list)
                    Quant.quants_move(quants, move,
                                      operation.location_dest_id,
                                      location_from=operation.location_id,
                                      lot_id=False,
                                      owner_id=operation.owner_id.id,
                                      src_package_id=operation.package_id.id,
                                      dest_package_id=quant_dest_package_id,
                                      entire_pack=entire_pack)
                else:
                    # Check what you can do with reserved quants already
                    qty_on_link = prout_move_qty[move]
                    rounding = operation.product_id.uom_id.rounding
                    for reserved_quant in move.reserved_quant_ids:
                        if (
                            (reserved_quant.owner_id.id !=
                             operation.owner_id.id) or
                            (reserved_quant.location_id.id !=
                             operation.location_id.id) or
                            (reserved_quant.package_id.id !=
                             operation.package_id.id)):
                            continue
                        if not reserved_quant.lot_id:
                            false_quants += [reserved_quant]
                        elif float_compare(
                            lot_quantities.get(reserved_quant.lot_id.id, 0),
                                0, precision_rounding=rounding) > 0:
                            if float_compare(
                                lot_quantities[reserved_quant.lot_id.id],
                                reserved_quant.qty,
                                    precision_rounding=rounding) >= 0:
                                lot_quantities[reserved_quant.lot_id.id] -= \
                                    reserved_quant.qty
                                quants_taken += [
                                    (reserved_quant, reserved_quant.qty)]
                                qty_on_link -= reserved_quant.qty
                            else:
                                quants_taken += [
                                    (reserved_quant,
                                     lot_quantities[reserved_quant.lot_id.id])]
                                lot_quantities[reserved_quant.lot_id.id] = 0
                                qty_on_link -= lot_quantities[
                                    reserved_quant.lot_id.id]
                    lot_move_qty[move.id] = qty_on_link

                remaining_move_qty[move.id] -= prout_move_qty[move]

            # Handle lots separately
            if operation.pack_lot_ids:
                # TDE FIXME: fix call to move_quants_by_lot to ease
                # understanding
                self._move_quants_by_lot(
                    operation, lot_quantities, quants_taken,
                    false_quants, lot_move_qty, quant_dest_package_id)

            # Handle pack in pack
            if (not operation.product_id and operation.package_id and
                operation.result_package_id.id !=
                    operation.package_id.parent_id.id):
                operation.package_id.sudo().write(
                    {'parent_id': operation.result_package_id.id})

        # Check for remaining qtys and unreserve/check move_dest_id in
        move_dest_ids = set()
        for move in self:
            if float_compare(
                remaining_move_qty[move.id], 0,
                    precision_rounding=move.product_id.uom_id.rounding) > 0:
                # TDE: do in batch ? redone ? check this
                move.check_tracking(False)

                preferred_domain_list = [
                    [('reservation_id', '=', move.id)],
                    [('reservation_id', '=', False)],
                    ['&', ('reservation_id', '!=', move.id),
                     ('reservation_id', '!=', False)]]
                quants = Quant.quants_get_preferred_domain(
                    remaining_move_qty[move.id], move,
                    domain=[('qty', '>', 0)],
                    preferred_domain_list=preferred_domain_list)
                Quant.quants_move(
                    quants, move, move.location_dest_id,
                    lot_id=move.restrict_lot_id.id,
                    owner_id=move.restrict_partner_id.id)

            # If the move has a destination, add it to the list to reserve
            if (move.move_dest_id and
                    move.move_dest_id.state in ('waiting', 'confirmed')):
                move_dest_ids.add(move.move_dest_id.id)

            if move.procurement_id:
                procurements |= move.procurement_id

            # unreserve the quants and make them available for other
            # operations/moves
            move.quants_unreserve()

        # Check the packages have been placed in the correct locations
        self.mapped('quant_ids').filtered(
            lambda quant: quant.package_id and quant.qty > 0).mapped(
                'package_id')._check_location_constraint()

        # NOTE VX: This section was overwritten.
        for move in self:
            if move.has_validate_picking_after_move_date():
                move_date = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            else:
                move_date = move.date
            move.write({'state': 'done', 'date': move_date})
        procurements.check()
        # assign destination moves
        if move_dest_ids:
            # TDE FIXME: record setise me
            self.browse(list(move_dest_ids)).action_assign()

        pickings.filtered(
            lambda picking: picking.state == 'done' and not
            picking.date_done).write(
                {'date_done': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})

        return True


class StockQuant(models.Model):

    _inherit = 'stock.quant'

    @api.multi
    def _quant_create_from_move(self, qty, move, lot_id=False, owner_id=False,
                                src_package_id=False, dest_package_id=False,
                                force_location_from=False,
                                force_location_to=False):
        if self._context.get('allow_past_date_quants', False):
            res = self._quant_create_allow_past_date(
                qty, move, lot_id=lot_id, owner_id=owner_id,
                src_package_id=src_package_id, dest_package_id=dest_package_id,
                force_location_from=force_location_from,
                force_location_to=force_location_to)
        else:
            res = super(StockQuant, self)._quant_create_from_move(
                qty, move, lot_id=lot_id, owner_id=owner_id,
                src_package_id=src_package_id, dest_package_id=dest_package_id,
                force_location_from=force_location_from,
                force_location_to=force_location_to)
        return res

    @api.multi
    def _quant_create_allow_past_date(
            self, qty, move, lot_id=False, owner_id=False,
            src_package_id=False, dest_package_id=False,
            force_location_from=False, force_location_to=False):
        """ NOTE: This method is a copy of the original one in odoo named
        _quant_create Here we set in_date taking into account the move date

        This method is call from the quant_move after action_done.

        Look for "# NOTE VX: This section was overwritten." to find the added
        code.
        """
        price_unit = move.get_price_unit()
        location = force_location_to or move.location_dest_id
        rounding = move.product_id.uom_id.rounding

        # NOTE VX: This is the new section that was overwritten
        if move.has_validate_picking_after_move_date():
            quant_date = datetime.now().strftime(
                DEFAULT_SERVER_DATETIME_FORMAT)
        else:
            quant_date = move.date

        vals = {
            'product_id': move.product_id.id,
            'location_id': location.id,
            'qty': float_round(qty, precision_rounding=rounding),
            'cost': price_unit,
            'history_ids': [(4, move.id)],
            'in_date': quant_date,
            'company_id': move.company_id.id,
            'lot_id': lot_id,
            'owner_id': owner_id,
            'package_id': dest_package_id,
        }

        if move.location_id.usage == 'internal':
            # if we were trying to move something from an internal location and
            # reach here (quant creation),
            # it means that a negative quant has to be created as well.
            negative_vals = vals.copy()
            negative_vals['location_id'] = (force_location_from.id
                                            if force_location_from
                                            else move.location_id.id)
            negative_vals['qty'] = float_round(-qty,
                                               precision_rounding=rounding)
            negative_vals['cost'] = price_unit
            negative_vals['negative_move_id'] = move.id
            negative_vals['package_id'] = src_package_id
            negative_quant_id = self.sudo().create(negative_vals)
            vals.update({'propagated_from_id': negative_quant_id.id})

        # create the quant as superuser, because we want to restrict the
        # creation of quant manually: we should always use this method to
        # create quants
        quant_id = self.sudo().create(vals)
        return quant_id
