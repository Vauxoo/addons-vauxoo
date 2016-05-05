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

from openerp import models, api, SUPERUSER_ID, _
from openerp import osv
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

    def action_done(self, cr, uid, ids, context=None):
        context = context or {}
        if context.get('allow_past_date_quants', False):
            res = self.action_done_allow_past_date(cr, uid, ids,
                                                   context=context)
        else:
            res = super(StockMove, self).action_done(cr, uid, ids,
                                                     context=context)
        return res

    def action_done_allow_past_date(self, cr, uid, ids, context=None):
        """NOTE: This method is a copy of the original one in odoo named
        action_done but we add a new sectiond of conde to introduce exception
        on the test.

        Look for "# NOTE VX: This section was overwritten." to find the added
        code.
        """
        context = context or {}
        picking_obj = self.pool.get("stock.picking")
        quant_obj = self.pool.get("stock.quant")
        todo = [move.id for move in self.browse(
            cr, uid, ids, context=context) if move.state == "draft"]
        if todo:
            ids = self.action_confirm(cr, uid, todo, context=context)
        pickings = set()
        procurement_ids = set()
        # Search operations that are linked to the moves
        operations = set()
        move_qty = {}
        for move in self.browse(cr, uid, ids, context=context):
            move_qty[move.id] = move.product_qty
            for link in move.linked_move_operation_ids:
                operations.add(link.operation_id)

        # Sort operations according to entire packages first, then package +
        # lot, package only, lot only
        operations = list(operations)
        operations.sort(key=lambda x: (
            (x.package_id and not x.product_id) and -4 or 0) + (
                x.package_id and -2 or 0) + (x.lot_id and -1 or 0))

        for ops in operations:
            if ops.picking_id:
                pickings.add(ops.picking_id.id)
            main_domain = [('qty', '>', 0)]
            for record in ops.linked_move_operation_ids:
                move = record.move_id
                self.check_tracking(
                    cr, uid, move, not ops.product_id and ops.package_id.id or
                    ops.lot_id.id, context=context)
                prefered_domain = [('reservation_id', '=', move.id)]
                fallback_domain = [('reservation_id', '=', False)]
                fallback_domain2 = ['&',
                                    ('reservation_id', '!=', move.id),
                                    ('reservation_id', '!=', False)]
                prefered_domain_list = \
                    [prefered_domain] + [fallback_domain] + [fallback_domain2]
                dom = main_domain + self.pool.get(
                    'stock.move.operation.link').get_specific_domain(
                        cr, uid, record, context=context)
                quants = quant_obj.quants_get_prefered_domain(
                    cr, uid, ops.location_id, move.product_id, record.qty,
                    domain=dom, prefered_domain_list=prefered_domain_list,
                    restrict_lot_id=move.restrict_lot_id.id,
                    restrict_partner_id=move.restrict_partner_id.id,
                    context=context)
                if ops.product_id:
                    # If a product is given, the result is always put
                    # immediately in the result package (if it is False, they
                    # are without package)
                    quant_dest_package_id = ops.result_package_id.id
                    ctx = context
                else:
                    # When a pack is moved entirely, the quants should not be
                    # written anything for the destination package
                    quant_dest_package_id = False
                    ctx = context.copy()
                    ctx['entire_pack'] = True
                quant_obj.quants_move(
                    cr, uid, quants, move, ops.location_dest_id,
                    location_from=ops.location_id, lot_id=ops.lot_id.id,
                    owner_id=ops.owner_id.id, src_package_id=ops.package_id.id,
                    dest_package_id=quant_dest_package_id, context=ctx)

                # Handle pack in pack
                if (not ops.product_id and ops.package_id and
                        ops.result_package_id.id !=
                        ops.package_id.parent_id.id):
                    self.pool.get('stock.quant.package').write(
                        cr, SUPERUSER_ID, [ops.package_id.id], {
                            'parent_id': ops.result_package_id.id},
                        context=context)
                if not move_qty.get(move.id):
                    raise osv.except_osv(
                        _("Error"),
                        _("The roundings of your Unit of Measures %s on the"
                          " move vs. %s on the product don't allow to do"
                          " these operations or you are not transferring the"
                          " picking at once. ") % (
                              move.product_uom.name,
                              move.product_id.uom_id.name))
                move_qty[move.id] -= record.qty
        # Check for remaining qtys and unreserve/check move_dest_id in
        move_dest_ids = set()
        for move in self.browse(cr, uid, ids, context=context):
            move_qty_cmp = float_compare(
                move_qty[move.id], 0,
                precision_rounding=move.product_id.uom_id.rounding)
            if move_qty_cmp > 0:  # (=In case no pack operations in picking)
                main_domain = [('qty', '>', 0)]
                prefered_domain = [('reservation_id', '=', move.id)]
                fallback_domain = [('reservation_id', '=', False)]
                fallback_domain2 = ['&', ('reservation_id', '!=', move.id),
                                    ('reservation_id', '!=', False)]
                prefered_domain_list = \
                    [prefered_domain] + [fallback_domain] + [fallback_domain2]
                self.check_tracking(cr, uid, move, move.restrict_lot_id.id,
                                    context=context)
                qty = move_qty[move.id]

                quants = quant_obj.quants_get_prefered_domain(
                    cr, uid, move.location_id, move.product_id, qty,
                    domain=main_domain,
                    prefered_domain_list=prefered_domain_list,
                    restrict_lot_id=move.restrict_lot_id.id,
                    restrict_partner_id=move.restrict_partner_id.id,
                    context=context)

                quant_obj.quants_move(
                    cr, uid, quants, move, move.location_dest_id,
                    lot_id=move.restrict_lot_id.id,
                    owner_id=move.restrict_partner_id.id, context=context)

            # If the move has a destination, add it to the list to reserve
            if (move.move_dest_id and
                    move.move_dest_id.state in ('waiting', 'confirmed')):
                move_dest_ids.add(move.move_dest_id.id)

            if move.procurement_id:
                procurement_ids.add(move.procurement_id.id)

            # unreserve the quants and make them available for other
            # operations/moves
            quant_obj.quants_unreserve(cr, uid, move, context=context)

        # Check the packages have been placed in the correct locations
        self._check_package_from_moves(cr, uid, ids, context=context)
        # set the move as done

        # NOTE VX: This section was overwritten.
        for move in self.browse(cr, uid, ids, context=context):
            if move.has_validate_picking_after_move_date():
                move_date = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            else:
                move_date = move.date
            self.write(
                cr, uid, [move.id], {'state': 'done', 'date': move_date},
                context=context)

        self.pool.get('procurement.order').check(
            cr, uid, list(procurement_ids), context=context)
        # assign destination moves
        if move_dest_ids:
            self.action_assign(cr, uid, list(move_dest_ids), context=context)
        # check picking state to set the date_done is needed
        done_picking = []
        for picking in picking_obj.browse(
                cr, uid, list(pickings), context=context):
            if picking.state == 'done' and not picking.date_done:
                done_picking.append(picking.id)
        if done_picking:
            picking_obj.write(
                cr, uid, done_picking,
                {'date_done': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)},
                context=context)
        return True


class StockQuant(models.Model):

    _inherit = 'stock.quant'

    def _quant_create(
            self, cr, uid, qty, move, lot_id=False, owner_id=False,
            src_package_id=False, dest_package_id=False,
            force_location_from=False, force_location_to=False,
            context=None):
        context = context or {}
        if context.get('allow_past_date_quants', False):
            res = self._quant_create_allow_past_date(
                cr, uid, qty, move, lot_id=lot_id, owner_id=owner_id,
                src_package_id=src_package_id, dest_package_id=dest_package_id,
                force_location_from=force_location_from,
                force_location_to=force_location_to, context=context)
        else:
            res = super(StockQuant, self)._quant_create(
                cr, uid, qty, move, lot_id=lot_id, owner_id=owner_id,
                src_package_id=src_package_id, dest_package_id=dest_package_id,
                force_location_from=force_location_from,
                force_location_to=force_location_to, context=context)
        return res

    def _quant_create_allow_past_date(
            self, cr, uid, qty, move, lot_id=False, owner_id=False,
            src_package_id=False, dest_package_id=False,
            force_location_from=False, force_location_to=False,
            context=None):
        """ NOTE: This method is a copy of the original one in odoo named
        _quant_create Here we set in_date taking into account the move date

        This method is call from the quant_move after action_done.

        Look for "# NOTE VX: This section was overwritten." to find the added
        code.
        """
        if context is None:
            context = {}
        price_unit = self.pool.get('stock.move').get_price_unit(
            cr, uid, move, context=context)
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
            negative_vals['location_id'] = \
                force_location_from and force_location_from.id \
                or move.location_id.id
            negative_vals['qty'] = float_round(-qty,
                                               precision_rounding=rounding)
            negative_vals['cost'] = price_unit
            negative_vals['negative_move_id'] = move.id
            negative_vals['package_id'] = src_package_id
            negative_quant_id = self.create(cr, SUPERUSER_ID, negative_vals,
                                            context=context)
            vals.update({'propagated_from_id': negative_quant_id})

        # create the quant as superuser, because we want to restrict the
        # creation of quant manually: we should always use this method to
        # create quants
        quant_id = self.create(cr, SUPERUSER_ID, vals, context=context)
        return self.browse(cr, uid, quant_id, context=context)
