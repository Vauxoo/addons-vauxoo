from odoo import fields, models, _
from odoo.tools.float_utils import float_compare, float_round
from odoo.exceptions import UserError


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    # pylint: disable=too-many-nested-blocks
    # pylint: disable=too-complex
    def _action_done(self):
        """NOTE: This method is a copy of the original one in odoo named action_done but we add
        a new section of code to introduce exception on the test.

        Look for "# NOTE VX: This section was overwritten." to find the added
        code.
        """
        if not self._context.get('allow_past_date_quants'):
            return super(StockMoveLine, self)._action_done()

        quant_obj = self.env['stock.quant']

        # First, we loop over all the move lines to do a preliminary check: `qty_done` should not
        # be negative and, according to the presence of a picking type or a linked inventory
        # adjustment, enforce some rules on the `lot_id` field. If `qty_done` is null, we unlink
        # the line. It is mandatory in order to free the reservation and correctly apply
        # `action_done` on the next move lines.
        ml_to_delete = self.env['stock.move.line']
        for ml in self:
            # Check here if `ml.qty_done` respects the rounding of `ml.product_uom_id`.
            uom_qty = float_round(ml.qty_done, precision_rounding=ml.product_uom_id.rounding,
                                  rounding_method='HALF-UP')
            precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            qty_done = float_round(ml.qty_done, precision_digits=precision_digits, rounding_method='HALF-UP')
            if float_compare(uom_qty, qty_done, precision_digits=precision_digits) != 0:
                raise UserError(_('The quantity done for the product "%s" doesn\'t respect the rounding precision \
                                  defined on the unit of measure "%s". Please change the quantity done or the \
                                  rounding precision of your unit of measure.') % (ml.product_id.display_name,
                                                                                   ml.product_uom_id.name))

            qty_done_float_compared = float_compare(ml.qty_done, 0, precision_rounding=ml.product_uom_id.rounding)
            if qty_done_float_compared > 0:
                if ml.product_id.tracking != 'none':
                    picking_type_id = ml.move_id.picking_type_id
                    if picking_type_id:
                        if picking_type_id.use_create_lots:
                            # If a picking type is linked, we may have to create a production lot on
                            # the fly before assigning it to the move line if the user checked both
                            # `use_create_lots` and `use_existing_lots`.
                            if ml.lot_name and not ml.lot_id:
                                lot = self.env['stock.production.lot'].create(
                                    {'name': ml.lot_name, 'product_id': ml.product_id.id}
                                )
                                ml.write({'lot_id': lot.id})
                        elif not picking_type_id.use_create_lots and not picking_type_id.use_existing_lots:
                            # If the user disabled both `use_create_lots` and `use_existing_lots`
                            # checkboxes on the picking type, he's allowed to enter tracked
                            # products without a `lot_id`.
                            continue
                    elif ml.move_id.inventory_id:
                        # If an inventory adjustment is linked, the user is allowed to enter
                        # tracked products without a `lot_id`.
                        continue

                    if not ml.lot_id:
                        raise UserError(_(
                            'You need to supply a Lot/Serial number for product %s.') % ml.product_id.display_name)
            elif qty_done_float_compared < 0:
                raise UserError(_('No negative quantities allowed'))
            else:
                ml_to_delete |= ml
        ml_to_delete.unlink()

        # Now, we can actually move the quant.
        done_ml = self.env['stock.move.line']
        for ml in self - ml_to_delete:
            if ml.product_id.type == 'product':
                rounding = ml.product_uom_id.rounding

                # if this move line is force assigned, unreserve elsewhere if needed
                if not ml.location_id.should_bypass_reservation() and float_compare(
                        ml.qty_done, ml.product_uom_qty, precision_rounding=rounding) > 0:
                    qty_done_product_uom = ml.product_uom_id._compute_quantity(
                        ml.qty_done, ml.product_id.uom_id, rounding_method='HALF-UP')
                    extra_qty = qty_done_product_uom - ml.product_qty
                    ml._free_reservation(ml.product_id, ml.location_id, extra_qty, lot_id=ml.lot_id,
                                         package_id=ml.package_id, owner_id=ml.owner_id, ml_to_ignore=done_ml)
                # unreserve what's been reserved
                if (not ml.location_id.should_bypass_reservation() and ml.product_id.type == 'product'
                        and ml.product_qty):
                    try:
                        quant_obj._update_reserved_quantity(
                            ml.product_id, ml.location_id, -ml.product_qty, lot_id=ml.lot_id,
                            package_id=ml.package_id, owner_id=ml.owner_id, strict=True)
                    except UserError:
                        quant_obj._update_reserved_quantity(
                            ml.product_id, ml.location_id, -ml.product_qty, lot_id=False,
                            package_id=ml.package_id, owner_id=ml.owner_id, strict=True)

                # move what's been actually done
                quantity = ml.product_uom_id._compute_quantity(
                    ml.qty_done, ml.move_id.product_id.uom_id, rounding_method='HALF-UP')

                # NOTE VX: This section was overwritten.
                ml_date = ml.date
                if ml.move_id.has_validate_picking_after_move_date():
                    ml_date = False
                available_qty, in_date = quant_obj._update_available_quantity(
                    ml.product_id, ml.location_id, -quantity, lot_id=ml.lot_id,
                    package_id=ml.package_id, owner_id=ml.owner_id, in_date=ml_date)
                # NOTE VX: End of overwrite.

                if available_qty < 0 and ml.lot_id:
                    # see if we can compensate the negative quants with some untracked quants
                    untracked_qty = quant_obj._get_available_quantity(
                        ml.product_id, ml.location_id, lot_id=False, package_id=ml.package_id,
                        owner_id=ml.owner_id, strict=True)
                    if untracked_qty:
                        taken_from_untracked_qty = min(untracked_qty, abs(quantity))
                        quant_obj._update_available_quantity(
                            ml.product_id, ml.location_id, -taken_from_untracked_qty, lot_id=False,
                            package_id=ml.package_id, owner_id=ml.owner_id)
                        quant_obj._update_available_quantity(
                            ml.product_id, ml.location_id, taken_from_untracked_qty, lot_id=ml.lot_id,
                            package_id=ml.package_id, owner_id=ml.owner_id)
                quant_obj._update_available_quantity(
                    ml.product_id, ml.location_dest_id, quantity, lot_id=ml.lot_id,
                    package_id=ml.result_package_id, owner_id=ml.owner_id, in_date=in_date)

            done_ml |= ml
        # Reset the reserved quantity as we just moved it to the destination location.
        # NOTE VX: This section was overwritten.
        date_now = fields.Datetime.now()
        for ml in self - ml_to_delete:
            ml_date = ml.date
            if ml.move_id.has_validate_picking_after_move_date():
                ml_date = date_now
            ml.with_context(bypass_reservation_update=True).write({
                'product_uom_qty': 0.00,
                'date': ml_date,
            })
