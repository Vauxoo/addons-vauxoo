# coding: utf-8

from openerp import models, fields, api
from openerp import SUPERUSER_ID
from openerp.tools.float_utils import float_compare, float_round, float_is_zero
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime
import openerp.addons.decimal_precision as dp
import logging

_logger = logging.getLogger(__name__)

SEGMENTATION_COST = [
    'landed_cost',
    'subcontracting_cost',
    'material_cost',
    'production_cost',
]


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.v7
    def action_done(self, cr, uid, ids, context=None):
        sgmnt = self.product_segmentation_fetch_before_done(
            cr, uid, ids, context=context)
        res = super(StockMove, self).action_done(cr, uid, ids, context=context)
        self.product_segmentation_update_after_done(
            cr, uid, ids, sgmnt, context=context)
        return res

    @api.v7
    def product_segmentation_fetch_before_done(
            self, cr, uid, ids, context=None):
        """Fetch standard_price and segmentation cost for every product that was
        purchased and is average costing method prior to change its values.
        Returns a dictionary.
        """
        res = {}
        precision = self.pool.get('decimal.precision').precision_get(
            cr, uid, 'Account')
        for move in self.browse(cr, uid, ids, context=context):
            # adapt standard price on incoming moves if the product
            # cost_method is 'average'
            if move.location_id.usage == 'supplier' and \
                    move.product_id.cost_method == 'average':
                std = move.product_id.standard_price
                qty_available = move.product_id.product_tmpl_id.qty_available
                prod_id = move.product_id.id
                if prod_id not in res:
                    # /!\ TODO: Fetch segmentation for product
                    sgmnt = {}
                    res[prod_id] = {}
                    res[prod_id]['qty'] = qty_available
                    res[prod_id]['standard_price'] = std
                    sum_sgmnt = 0.0
                    for fieldname in SEGMENTATION_COST:
                        fn_cost = getattr(move.product_id, fieldname)
                        sum_sgmnt += fn_cost
                        sgmnt[fieldname] = fn_cost
                    if not sum_sgmnt or \
                            not float_is_zero(sum_sgmnt - std, precision):
                        sgmnt = {}.fromkeys(SEGMENTATION_COST, 0.0)
                        res[prod_id].update(sgmnt)
                        res[prod_id]['material_cost'] = std
                    else:
                        res[prod_id].update(sgmnt)
        return res

    @api.v7
    def product_segmentation_update_after_done(
            self, cr, uid, ids, sgmnt, context=None):
        """Computes segmentation values on average product based on previous
        values stored before action_done method is applied
        """
        context = dict(context or {})
        product_obj = self.pool.get('product.product')
        res = {}
        for prod_id in sgmnt:
            prod_brw = product_obj.browse(cr, uid, prod_id, context=context)
            std = prod_brw.standard_price
            qty = prod_brw.product_tmpl_id.qty_available
            if qty <= 0:
                # /!\ NOTE: Do not change anything
                continue

            res[prod_id] = {}
            diff = std * qty - \
                sgmnt[prod_id]['standard_price'] * sgmnt[prod_id]['qty']
            for fieldname in SEGMENTATION_COST:
                fn_cost = sgmnt[prod_id][fieldname] * sgmnt[prod_id]['qty']
                if fieldname == 'material_cost':
                    fn_cost += diff
                res[prod_id][fieldname] = fn_cost / qty

        # Write the standard price, as SUPERUSER_ID because a warehouse
        # manager may not have the right to write on products
        for prod_id in res:
            product_obj.write(
                cr, SUPERUSER_ID, [prod_id], res[prod_id], context=context)


class StockQuant(models.Model):
    _inherit = "stock.quant"

    @api.depends('material_cost', 'production_cost', 'landed_cost',
                 'subcontracting_cost')
    def _compute_segmentation(self):
        for record in self:
            record.segmentation_cost = sum([
                getattr(record, fn) for fn in SEGMENTATION_COST])

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

    def initializing_quant_segmentation(self):
        self._cr.execute('''
            SELECT
            COUNT(sq.id)
            FROM stock_quant AS sq
            INNER JOIN product_product AS pp ON sq.product_id = pp.id
            INNER JOIN product_template AS pt ON pt.id = pp.product_tmpl_id
            INNER JOIN ir_property AS ip1 ON (
            ip1.res_id = 'product.template,' || pt.id::text
            AND ip1.name = 'cost_method')
            LEFT JOIN ir_property AS ip2 ON (
            ip2.res_id = 'product.template,' || pt.id::text
            AND ip2.name = 'standard_price')
            WHERE
            sq.material_cost = 0
            AND sq.landed_cost = 0
            AND sq.production_cost = 0
            AND sq.subcontracting_cost = 0
            -- AND ip1.value_text = 'standard'  -- APPLY ONLY ON STANDARD
            ;''')
        res = self._cr.fetchone()
        _logger.info('%s quants are to be fixed', str(int(res[0])))

        _logger.info('Updating to zero quants with segment in NULL')
        self._cr.execute('''
            UPDATE stock_quant
            SET material_cost = 0.0000
            WHERE material_cost IS NULL;
            ;''')
        _logger.info('Material Cost with NULL has been updated')
        self._cr.execute('''
            UPDATE stock_quant
            SET landed_cost = 0.0000
            WHERE landed_cost IS NULL;
            ;''')
        _logger.info('Landed Cost with NULL has been updated')
        self._cr.execute('''
            UPDATE stock_quant
            SET production_cost = 0.0000
            WHERE production_cost IS NULL;
            ;''')
        _logger.info('Production Cost with NULL has been updated')
        self._cr.execute('''
            UPDATE stock_quant
            SET subcontracting_cost = 0.0000
            WHERE subcontracting_cost IS NULL;
            ;''')
        _logger.info('Subcontracting Cost with NULL has been updated')

        _logger.info('Setting Material Cost equal to Cost on Quant')
        self._cr.execute('''
            UPDATE stock_quant
            SET material_cost = cost
            WHERE
                cost != 0
                AND material_cost = 0
                AND landed_cost  = 0
                AND production_cost = 0
                AND subcontracting_cost = 0
            ;''')
        _logger.info('Material Cost equal to Cost on Quant has been set')

        _logger.info('Updating Segmentation Cost with sum of Segmentation')
        self._cr.execute('''
            UPDATE stock_quant
            SET segmentation_cost = (
                material_cost + landed_cost +
                production_cost + subcontracting_cost)
            WHERE
            material_cost != 0
            OR landed_cost != 0
            OR production_cost != 0
            OR subcontracting_cost != 0
            ;''')
        _logger.info('Segmentation Cost has been updated')

        self._cr.execute('''
            SELECT
            COUNT(sq.id)
            FROM stock_quant AS sq
            INNER JOIN product_product AS pp ON sq.product_id = pp.id
            INNER JOIN product_template AS pt ON pt.id = pp.product_tmpl_id
            INNER JOIN ir_property AS ip1 ON (
            ip1.res_id = 'product.template,' || pt.id::text
            AND ip1.name = 'cost_method')
            LEFT JOIN ir_property AS ip2 ON (
            ip2.res_id = 'product.template,' || pt.id::text
            AND ip2.name = 'standard_price')
            WHERE
            sq.material_cost = 0
            AND sq.landed_cost = 0
            AND sq.production_cost = 0
            AND sq.subcontracting_cost = 0
            -- AND ip1.value_text = 'standard'  -- APPLY ONLY ON STANDARD
            ;''')
        res = self._cr.fetchone()
        _logger.info('%s quants not fixed', str(int(res[0])))

        self._cr.execute('''
            SELECT COUNT(sq.id)
            FROM stock_quant AS sq
            INNER JOIN product_product AS pp ON pp.id = sq.product_id
            INNER JOIN product_template AS pt ON pt.id = pp.product_tmpl_id
            INNER JOIN ir_property AS ip1 ON (
                ip1.res_id = 'product.template,' || pt.id::text
                AND ip1.name = 'cost_method')
            INNER JOIN ir_property AS ip2 ON (
                ip2.res_id = 'product.template,' || pt.id::text
                AND ip2.name = 'standard_price')
            WHERE
            sq.cost = 0
            AND sq.material_cost = 0
            AND sq.landed_cost = 0
            AND sq.production_cost = 0
            AND sq.subcontracting_cost = 0
            AND ip1.value_text = 'standard'  -- APPLY ONLY ON STANDARD
            AND ip2.value_float != 0
            -- DO NOT LOSE TIME TRYING TO UPDATE WITH ZERO
            ;''')
        res = self._cr.fetchone()
        _logger.info(
            '%s quants that can be fixed from Product that are STD',
            str(int(res[0])))

        _logger.info(
            'Updating quants that can be fixed from Product that are STD')
        self._cr.execute('''
            UPDATE stock_quant
            SET material_cost = ip2.value_float,
                segmentation_cost = ip2.value_float
            FROM product_product AS pp
            INNER JOIN product_template AS pt ON pt.id = pp.product_tmpl_id
            INNER JOIN ir_property AS ip1 ON (
                ip1.res_id = 'product.template,' || pt.id::text
                AND ip1.name = 'cost_method')
            INNER JOIN ir_property AS ip2 ON (
                ip2.res_id = 'product.template,' || pt.id::text
                AND ip2.name = 'standard_price')
            WHERE
            stock_quant.cost = 0
            AND stock_quant.product_id = pp.id
            AND stock_quant.material_cost = 0
            AND stock_quant.landed_cost  = 0
            AND stock_quant.production_cost = 0
            AND stock_quant.subcontracting_cost = 0
            AND ip1.value_text = 'standard'  -- APPLY ONLY ON STANDARD
            AND ip2.value_float != 0
            -- DO NOT LOSE TIME TRYING TO UPDATE WITH ZERO
            ;''')
        _logger.info(
            'Quants that could be fixed from Product and are STD were updated')

        self._cr.execute('''
            SELECT
            DISTINCT product_id,
            pt.name,
            ip1.value_text as cost_method
            FROM stock_quant AS sq
            INNER JOIN product_product AS pp ON sq.product_id = pp.id
            INNER JOIN product_template AS pt ON pt.id = pp.product_tmpl_id
            INNER JOIN ir_property AS ip1 ON (ip1.res_id = 'product.template,'
            || pt.id::text AND ip1.name = 'cost_method')
            LEFT JOIN ir_property AS ip2 ON (
                ip2.res_id = 'product.template,' || pt.id::text
                AND ip2.name = 'standard_price')
            WHERE
            sq.material_cost = 0
            AND sq.landed_cost  = 0
            AND sq.production_cost = 0
            AND sq.subcontracting_cost = 0
            AND ip1.value_text = 'standard'  -- APPLY ONLY ON STANDARD
            ;''')
        res = self._cr.fetchall()
        if res:
            _logger.warning('Products that have standard_price in zero')
        for prod_id, name, cost_method in res:
            _logger.warning('%s, %s, %s', str(prod_id), name, cost_method)

    @api.v7
    def _quant_create(
            self, cr, uid, qty, move, lot_id=False, owner_id=False,
            src_package_id=False, dest_package_id=False,
            force_location_from=False, force_location_to=False, context=None):
        """Create a quant in the destination location and create a negative quant
        in the source location if it's an internal location.
        """
        if context is None:
            context = {}
        price_unit = self.pool.get('stock.move').get_price_unit(
            cr, uid, move, context=context)
        location = force_location_to or move.location_dest_id
        rounding = move.product_id.uom_id.rounding
        vals = {
            'product_id': move.product_id.id,
            'location_id': location.id,
            'qty': float_round(qty, precision_rounding=rounding),
            'cost': price_unit,
            'history_ids': [(4, move.id)],
            'in_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
            'company_id': move.company_id.id,
            'lot_id': lot_id,
            'owner_id': owner_id,
            'package_id': dest_package_id,
        }
        if move.purchase_line_id or move.inventory_id:
            vals.update({'material_cost': price_unit})

        if move.location_id.usage == 'internal':
            # if we were trying to move something from an internal location and
            # reach here (quant creation), it means that a negative quant has
            # to be created as well.

            exclude_ids = []
            query1 = """
                SELECT sq.id AS id, sq.propagated_from_id AS from_id
                FROM stock_quant AS sq
                WHERE
                    product_id = {product_id}
                    AND sq.propagated_from_id IS NOT NULL
            """.format(product_id=move.product_id.id)
            cr.execute(query1)
            for val in cr.fetchall():
                exclude_ids += list(val)

            if exclude_ids:
                exclude_ids = ', '.join(str(ex_ids) for ex_ids in exclude_ids)
                exclude_ids = ' AND sq.id NOT IN ({exclude_ids})'.format(
                    exclude_ids=exclude_ids)
            else:
                exclude_ids = ''

            query2 = """
                SELECT
                    sq.id,
                    sq.material_cost,
                    sq.landed_cost,
                    sq.production_cost,
                    sq.subcontracting_cost
                FROM stock_quant AS sq
                WHERE
                    product_id = {product_id}
                    AND qty > 0.0
                    {exclude_ids}
                ORDER BY sq.in_date DESC
                LIMIT 1
            """.format(
                product_id=move.product_id.id,
                exclude_ids=exclude_ids)
            cr.execute(query2)

            res = cr.dictfetchone()
            if res:
                del res['id']
                vals.update(res)
            # TODO: What about when no value is fetched. Could use cost?

            negative_vals = vals.copy()
            negative_vals['location_id'] = force_location_from and \
                force_location_from.id or move.location_id.id
            negative_vals['qty'] = float_round(
                -qty, precision_rounding=rounding)
            negative_vals['cost'] = price_unit
            negative_vals['negative_move_id'] = move.id
            negative_vals['package_id'] = src_package_id
            negative_quant_id = self.create(
                cr, SUPERUSER_ID, negative_vals, context=context)
            vals.update({'propagated_from_id': negative_quant_id})

        # create the quant as superuser, because we want to restrict the
        # creation of quant manually: we should always use this method to
        # create quants
        quant_id = self.create(cr, SUPERUSER_ID, vals, context=context)
        quant_brw = self.browse(cr, uid, quant_id, context=context)
        if move.product_id.valuation == 'real_time':
            self._account_entry_move(cr, uid, [quant_brw], move, context)
        return quant_brw

    @api.v7
    def _price_update_segmentation(
            self, cr, uid, ids, newprice, solving_quant, context=None):
        self._price_update(cr, uid, ids, newprice, context=context)
        sgmnt_dict = {}.fromkeys(SEGMENTATION_COST, 0.0)
        for fn in SEGMENTATION_COST:
            sgmnt_dict[fn] = getattr(solving_quant, fn)
        self.write(cr, SUPERUSER_ID, ids, sgmnt_dict, context=context)
        return True

    @api.v7
    def _quant_reconcile_negative(self, cr, uid, quant, move, context=None):
        """When new quant arrive in a location, try to reconcile it with
            negative quants. If it's possible, apply the cost of the new
            quant to the counter-part of the negative quant.
        """
        solving_quant = quant
        dom = [('qty', '<', 0)]
        if quant.lot_id:
            dom += [('lot_id', '=', quant.lot_id.id)]
        dom += [('owner_id', '=', quant.owner_id.id)]
        dom += [('package_id', '=', quant.package_id.id)]
        dom += [('id', '!=', quant.propagated_from_id.id)]
        quants = self.quants_get(
            cr, uid, quant.location_id, quant.product_id, quant.qty, dom,
            context=context)
        product_uom_rounding = quant.product_id.uom_id.rounding
        context = dict(context or {})
        context.update({'force_unlink': True})
        for quant_neg, qty in quants:
            if not quant_neg or not solving_quant:
                continue
            to_solve_quant_ids = self.search(
                cr, uid, [('propagated_from_id', '=', quant_neg.id)],
                context=context)
            if not to_solve_quant_ids:
                continue
            solving_qty = qty
            solved_quant_ids = []
            for to_solve_quant in self.browse(
                    cr, uid, to_solve_quant_ids, context=context):
                if float_compare(
                        solving_qty, 0,
                        precision_rounding=product_uom_rounding) <= 0:
                    continue
                solved_quant_ids.append(to_solve_quant.id)
                self._quant_split(
                    cr, uid, to_solve_quant,
                    min(solving_qty, to_solve_quant.qty), context=context)
                solving_qty -= min(solving_qty, to_solve_quant.qty)
            remaining_solving_quant = self._quant_split(
                cr, uid, solving_quant, qty, context=context)
            remaining_neg_quant = self._quant_split(
                cr, uid, quant_neg, -qty, context=context)
            # if the reconciliation was not complete, we need to link together
            # the remaining parts
            if remaining_neg_quant:
                remaining_to_solve_quant_ids = self.search(
                    cr, uid,
                    [('propagated_from_id', '=', quant_neg.id),
                     ('id', 'not in', solved_quant_ids)],
                    context=context)
                if remaining_to_solve_quant_ids:
                    self.write(
                        cr, SUPERUSER_ID, remaining_to_solve_quant_ids,
                        {'propagated_from_id': remaining_neg_quant.id},
                        context=context)
            if solving_quant.propagated_from_id and solved_quant_ids:
                self.write(
                    cr, SUPERUSER_ID, solved_quant_ids,
                    {'propagated_from_id':
                     solving_quant.propagated_from_id.id},
                    context=context)
            # delete the reconciled quants, as it is replaced by the solved
            # quants
            self.unlink(cr, SUPERUSER_ID, [quant_neg.id], context=context)
            if solved_quant_ids:
                # price update + accounting entries adjustments
                self._price_update_segmentation(
                    cr, uid, solved_quant_ids, solving_quant.cost,
                    solving_quant, context=context)
                # merge history (and cost?)
                self._quants_merge(
                    cr, uid, solved_quant_ids, solving_quant, context=context)
            self.unlink(cr, SUPERUSER_ID, [solving_quant.id], context=context)
            solving_quant = remaining_solving_quant
