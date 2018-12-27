# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.
# from odoo.tools import float_round
#from odoo.tools.float_utils import float_compare, float_round, float_is_zero
import logging
from odoo.addons import decimal_precision as dp
from odoo import fields, models, api

_logger = logging.getLogger(__name__)


SEGMENTATION_COST = [
    'landed_cost',
    'subcontracting_cost',
    'material_cost',
    'production_cost',
]


class HistoricalStockMove(models.Model):
    _name = 'historical.stock.move'

    move_id = fields.Many2one(
        'stock.move', 'Move',
        index=True,
        help='Validated move')
    origin_move_id = fields.Many2one(
        'stock.move',
        'Consumed Move',
        index=True,
        help='The move whose lot or cost '
        'was used to fulfill the validated move')
    cost = fields.Float(
        related='origin_move_id.price_unit',
        store=True)
    product_id = fields.Many2one(
        related='origin_move_id.product_id',
        store=True,
        index=True)
    product_uom = fields.Many2one(
        related='move_id.product_uom')
    quantity = fields.Float(
        digits=dp.get_precision('Product Unit of Measure'),
        help="Quantity used from the consumed move")
    date = fields.Datetime(help="Validation Move Date")

    valuation_type = fields.Selection(
        [('financial', 'Financial'),
         ('logistic', 'Logistic')],
        index=True)


class StockMove(models.Model):

    _inherit = 'stock.move'

    logistic_remaining_qty = fields.Float(
        copy=False,
        help="Quantity to be consume when the "
        "product is moved from a specific warehouse")
    logistic_remaining_value = fields.Float(
        copy=False)

    move_orig_financial_ids = fields.One2many(
        'historical.stock.move', 'move_id', 'Original Fifo Move',
        domain=[('valuation_type', '=', 'financial')],
        help="Optional: previous stock move when chaining them")

    move_orig_logistic_ids = fields.One2many(
        'historical.stock.move', 'move_id', 'Original Logistic Move',
        domain=[('valuation_type', '=', 'logistic')],
        help="Optional: previous stock move when chaining them")

    material_cost = fields.Float(
        string='Material Cost',
        digits=dp.get_precision('Account'))

    production_cost = fields.Float(
        string='Production Cost',
        digits=dp.get_precision('Account'))
    subcontracting_cost = fields.Float(
        string='Subcontracting Cost',
        digits=dp.get_precision('Account'))
    landed_cost = fields.Float(
        string='Landed Cost',
        digits=dp.get_precision('Account'))
    segmentation_cost = fields.Float(
        string='Actual Cost', store=True, readonly=True,
        compute='_compute_segmentation',
        digits=dp.get_precision('Account'),
        help=("Provides the actual cost for this transaction. "
              "It is computed from the sum of the segmentation costs: "
              "`material cost`, `subcontracting cost`, `landed cost` "
              "& `production cost`"))

    # ################# Quant Cost Segmentation ###############################

    def initializing_stock_segmentation(self):
        """Setting segmentation fields"""
        _logger.info('Updating to zero quants with segment in NULL')
        self.env.cr.execute('''
            UPDATE
                stock_move
            SET
                material_cost = CASE WHEN material_cost IS NULL
                    THEN 0.0 ELSE material_cost END,
                production_cost = CASE WHEN production_cost IS NULL
                THEN 0.0 ELSE production_cost END,
                subcontracting_cost = CASE WHEN subcontracting_cost IS NULL
                THEN 0.0 ELSE subcontracting_cost END,
                landed_cost = CASE WHEN landed_cost IS NULL
                THEN 0.0 ELSE landed_cost END
            WHERE
                material_cost IS NULL OR
                production_cost IS NULL OR
                subcontracting_cost IS NULL OR
                landed_cost IS NULL
            ;''')
        _logger.info('Setting Material Cost equal to Cost on Quant')
        self.env.cr.execute('''
            UPDATE
                stock_move
            SET material_cost = price_unit
            WHERE
                price_unit > 0
                AND material_cost = 0
                AND landed_cost  = 0
                AND production_cost = 0
                AND subcontracting_cost = 0
            ;''')
        _logger.info('Material Cost equal to Cost on Quant has been set')

        _logger.info('Setting Logistic remaining value and qty')
        self.env.cr.execute('''
            UPDATE
                stock_move
            SET
                logistic_remaining_value = remaining_value,
                logistic_remaining_qty = remaining_qty
            WHERE
                remaining_value > 0
            ;''')
        _logger.info('Logistic remaining value and qty has been set')

        _logger.info('Updating Segmentation Cost with sum of Segmentation')
        self.env.cr.execute('''
            UPDATE
                stock_move
            SET
                segmentation_cost = (
                material_cost + landed_cost +
                production_cost + subcontracting_cost)
            WHERE
                material_cost != 0
                OR landed_cost != 0
                OR production_cost != 0
                OR subcontracting_cost != 0
            ;''')
        _logger.info('Segmentation Cost has been updated')

    @api.model
    def create(self, vals):
        """Adding the material cost if the move created is in type"""
        location = self.env['stock.location']
        location_id = location.browse(vals.get('location_id', 0))
        location_dest_id = location.browse(vals.get('location_dest_id', 0))
        if ((location_id.external or not
                location_id._should_be_valued()) and
                location_dest_id._should_be_valued()):
            vals['material_cost'] = vals.get('price_unit', 0)
        return super(StockMove, self).create(vals)

    @api.depends('material_cost', 'production_cost', 'landed_cost',
                 'subcontracting_cost')
    def _compute_segmentation(self):
        for record in self:
            record.segmentation_cost = sum([
                getattr(record, fn) for fn in SEGMENTATION_COST])


###############################################################################

    @api.model
    def _fifo_vacuum(self):
        """ Every moves that need to be fixed are identifiable by having a
        negative `remaining_qty`.
        """
        res = super(StockMove, self)._fifo_vacuum()
        for move in self.filtered(
                lambda m: (m._is_in() or m._is_out()) and m.remaining_qty < 0):
            domain = [
                ('logistic_remaining_qty', '>', 0),
                '|', ('date', '>', move.date),
                '&', ('date', '=', move.date),
                ('id', '>', move.id)
            ]
            domain += move._get_in_domain()
            candidates = self.search(domain, order='date, id')
            if not candidates:
                continue
            qty_to_take_on_candidates = abs(move.logistic_remaining_qty)
            qty_taken_on_candidates = 0
            tmp_value = 0
            for candidate in candidates:
                qty_taken_on_candidate = (
                    candidate.logistic_remaining_qty
                    if candidate.logistic_remaining_qty <=
                    qty_to_take_on_candidates
                    else qty_to_take_on_candidates)
                qty_taken_on_candidates += qty_taken_on_candidate

                value_taken_on_candidate = (
                    qty_taken_on_candidate * candidate.price_unit)
                candidate_vals = {
                    'logistic_remaining_qty':
                    candidate.logistic_remaining_qty - qty_taken_on_candidate,
                    'logistic_remaining_value':
                    candidate.logistic_remaining_value -
                    value_taken_on_candidate,
                }
                candidate.write(candidate_vals)

                qty_to_take_on_candidates -= qty_taken_on_candidate
                tmp_value += value_taken_on_candidate
                if qty_to_take_on_candidates == 0:
                    break

            new_logistic_remaining_qty = (
                move.logistic_remaining_qty + qty_taken_on_candidates)
            new_logistic_remaining_value = (
                new_logistic_remaining_qty * abs(move.price_unit))

            move.write({
                'logistic_remaining_value': new_logistic_remaining_value,
                'logistic_remaining_qty': new_logistic_remaining_qty,
            })
        return res

    def _run_valuation(self, quantity=None):
        self.ensure_one()
        res = super(StockMove, self)._run_valuation(quantity=quantity)
        if self._is_in():
            valued_move_lines = self.move_line_ids.filtered(
                lambda ml: not ml.location_id._should_be_valued() and
                ml.location_dest_id._should_be_valued() and not ml.owner_id)
            valued_quantity = 0
            for valued_move_line in valued_move_lines:
                valued_quantity += (
                    valued_move_line.product_uom_id._compute_quantity(
                        valued_move_line.qty_done, self.product_id.uom_id))

            vals = {}
            price_unit = self._get_price_unit()
            value = price_unit * (quantity or valued_quantity)
            vals = {
                'logistic_remaining_value':
                value if quantity is None else
                self.logistic_remaining_value + value,
            }
            vals['logistic_remaining_qty'] = (
                valued_quantity if quantity is None else
                self.logistic_remaining_qty + quantity)
        # ###### Quant Cost Segmentation ###################################
            vals['material_cost'] = price_unit
        ####################################################################

            self.write(vals)
        return res

    @api.model
    def _run_logistic_fifo(self, move, quantity=None):
        move.ensure_one()
        Trace = self.env['stock.traceability.report']
        MoveLine = self.env['stock.move.line']

        # Deal with possible move lines that do not impact the valuation.
        valued_move_lines = move.move_line_ids.filtered(
            lambda ml: ml.location_id._should_be_valued() and not
            ml.location_dest_id._should_be_valued() and not ml.owner_id)
        valued_quantity = 0
        for valued_move_line in valued_move_lines:
            valued_quantity += (
                valued_move_line.product_uom_id._compute_quantity(
                    valued_move_line.qty_done, move.product_id.uom_id))

        qty_to_take_on_candidates = quantity or valued_quantity
        # Gathering logistic moves
        sml_ids = move.move_line_ids.filtered(lambda a: a.lot_id)
        Historical = self.env['historical.stock.move']
        used = self.env['stock.move']
        for sml in sml_ids:
            lines = Trace.with_context(active_id=sml.lot_id.id,
                                       model='stock.production.lot',
                                       ttype='downstream').get_lines()
            track_ids = [line['model_id'] for line in lines]
            move_line = MoveLine.browse(track_ids)
            origin_moves = move_line.mapped('move_id').filtered(
                lambda a: a.logistic_remaining_qty > 0)
            for origin_move in origin_moves:
                real_qty = sml.product_uom_id._compute_quantity(
                    sml.qty_done, move.product_id.uom_id)
                vals = {
                    'move_id': move.id,
                    'origin_move_id': origin_move.id,
                    'cost': origin_move.price_unit,
                    'quantity': real_qty,
                    'date': fields.Datetime.now(),
                    'valuation_type': 'logistic'
                }
                candidate_price_unit = (
                    (origin_move.logistic_remaining_value /
                     origin_move.logistic_remaining_qty)
                    )
                value_taken_on_candidate = (
                    real_qty * candidate_price_unit)
                candidate_vals = {
                    'logistic_remaining_qty':
                    origin_move.logistic_remaining_qty - real_qty,
                    'logistic_remaining_value':
                    origin_move.logistic_remaining_value -
                    value_taken_on_candidate
                }
                origin_move.write(candidate_vals)
                qty_to_take_on_candidates -= real_qty
                used += origin_move
                Historical.create(vals)
        candidates = (
            move.product_id._get_fifo_logistic_candidates_in_move(
                move.warehouse_id or
                move.picking_type_id.warehouse_id) or
            move.product_id._get_fifo_candidates_in_move())
        candidates -= used

        # Without lots
        for candidate in candidates:
            if not qty_to_take_on_candidates or qty_to_take_on_candidates < 0:
                break
            qty_taken_on_candidate = (
                candidate.logistic_remaining_qty
                if candidate.logistic_remaining_qty <=
                qty_to_take_on_candidates
                else qty_to_take_on_candidates)

            candidate_price_unit = (
                candidate.logistic_remaining_value /
                candidate.logistic_remaining_qty
                if candidate.logistic_remaining_qty
                else candidate.remaining_value /
                candidate.remaining_qty)
            value_taken_on_candidate = (
                qty_taken_on_candidate * candidate_price_unit)
            vals = {
                'move_id': move.id,
                'origin_move_id': candidate.id,
                'cost': candidate.price_unit,
                'quantity': qty_taken_on_candidate,
                'date': fields.Datetime.now(),
                'valuation_type': 'logistic'
            }
            Historical.create(vals)
            candidate_vals = {
                'logistic_remaining_qty':
                candidate.logistic_remaining_qty - qty_taken_on_candidate,
                'logistic_remaining_value':
                candidate.logistic_remaining_value - value_taken_on_candidate,
            }
            candidate.write(candidate_vals)
            qty_to_take_on_candidates -= qty_taken_on_candidate

    @api.model
    def _run_fifo(self, move, quantity=None):
        candidates = move.product_id._get_fifo_candidates_in_move()
        candidate_to_take = {
            candidate.id: candidate.remaining_qty for candidate in candidates}
        res = super(StockMove, self)._run_fifo(move, quantity=quantity)
        Historical = self.env['historical.stock.move']
        # Gathering both(Financial, Logistic) moves

        needed_qty = move.product_uom_qty
        candidate_used = False
        for candidate_taken in candidates:
            if (candidate_taken.remaining_qty !=
                    candidate_to_take[candidate_taken.id]):
                candidate_used = candidate_taken
                used_qty = (
                    needed_qty
                    if needed_qty < candidate_to_take[candidate_taken.id]
                    else candidate_to_take[candidate_taken.id])
                vals = {
                    'move_id': move.id,
                    'origin_move_id': candidate_taken.id,
                    'cost': candidate_taken.price_unit,
                    'quantity': used_qty,
                    'date': fields.Datetime.now(),
                    'valuation_type': 'financial'
                }
                needed_qty -= used_qty
                Historical.create(vals)
        self._run_logistic_fifo(move, quantity)
        # Update the segmentation fields with the values of the last used
        # candidate, if any.
        if candidate_used and move.product_id.cost_method == 'fifo':
            seg_vals = {val: candidate_used[val] for val in SEGMENTATION_COST}
            move.product_id.sudo().write(seg_vals)
        return res

    def _is_in(self):
        """ Check if the move should be considered as entering the company so
        that the cost method will be able to apply the correct logic.

        :return: True if the move is entering the company else False
        """
        for move_line in self.move_line_ids.filtered(
                lambda ml: not ml.owner_id):
            if ((move_line.location_id.external or not
                    move_line.location_id._should_be_valued()) and
                    move_line.location_dest_id._should_be_valued()):
                return True
        return False

    def _is_out(self):
        """ Check if the move should be considered as leaving the company so
        that the cost method will be able to apply the correct logic.

        :return: True if the move is leaving the company else False
        """
        for move_line in self.move_line_ids.filtered(
                lambda ml: not ml.owner_id):
            if (move_line.location_id._should_be_valued() and
                    (move_line.location_dest_id.external or not
                     move_line.location_dest_id._should_be_valued())):
                return True
        return False

    def _account_entry_move(self):
        super(StockMove, self)._account_entry_move()
        if self._is_in():
            hist_obj = self.env['historical.stock.move']
            hist = hist_obj.search([
                ('move_id', 'in', self.move_orig_ids.ids)])
            if hist:
                hist_obj.create({
                    'move_id': self.id,
                    'origin_move_id': hist[0].move_id.id,
                    'valuation_type': 'logistic',
                    'date': self.date,
                    'quantity': self.product_uom_qty,
                })

    @api.multi
    def _get_landed_information(self):
        landed_obj = self.env['stock.landed.cost']
        landed = landed_obj.search([
            ('picking_ids', 'in', self.mapped(
                'move_orig_logistic_ids.origin_move_id.picking_id.id')),
            ('l10n_mx_edi_customs_number', '!=', False)])
        origin_moves = self.mapped('move_orig_ids').filtered(
            lambda move: move.id not in self.mapped('returned_move_ids').ids)
        if origin_moves and not landed:
            landed = origin_moves._get_landed_information()
        return landed


class StockLocation(models.Model):

    _inherit = 'stock.location'

    external = fields.Boolean(
        help="This field is used to consider this location like an external "
        "location(Customer, Supplier), no matter if it is internal. \n"
        "It means that valuation process will be executed when you send "
        "or receive products using this location as origin or destiny"
    )


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    @api.multi
    def write(self, vals):
        if 'qty_done' in vals:
            moves_to_update = {}
            for move_line in self.filtered(
                lambda ml: ml.state == 'done' and (
                    ml.move_id._is_in() or ml.move_id._is_out())):
                moves_to_update[move_line.move_id] = vals[
                    'qty_done'] - move_line.qty_done

            for move_id, qty_difference in moves_to_update.items():
                move_vals = {}
                if move_id._is_in():
                    correction_value = qty_difference * move_id.price_unit
                    move_vals['logistic_remaining_qty'] = (
                        move_id.logistic_remaining_qty + qty_difference)
                    move_vals['logistic_remaining_value'] = (
                        move_id.logistic_remaining_value + correction_value)
                elif move_id._is_out() and qty_difference < 0:
                    candidates_receipt = self.env['stock.move'].search(
                        move_id.product_id.
                        _get_fifo_logistic_candidates_in_move(
                            move_id.warehouse_id or
                            move_id.picking_type_id.warehouse_id),
                        order='date, id desc', limit=1)
                    if candidates_receipt:
                        candidates_receipt.write({
                            'logistic_remaining_qty':
                            candidates_receipt.logistic_remaining_qty +
                            -qty_difference,
                            'logistic_remaining_value':
                            candidates_receipt.logistic_remaining_value +
                            (-qty_difference * candidates_receipt.price_uniti)
                        })
                move_id.write(move_vals)
        return super(StockMoveLine, self).write(vals)
