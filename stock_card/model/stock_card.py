# coding: utf-8

from openerp import models, fields, api
import openerp.addons.decimal_precision as dp

# TODO: multi-company awareness to be developed


class StockCard(models.TransientModel):
    _name = 'stock.card'
    product_ids = fields.Many2many('product.product', string='Products')


class StockCardProduct(models.TransientModel):
    _name = 'stock.card.product'
    product_id = fields.Many2one('product.product', string='Product')
    stock_card_move_ids = fields.One2many(
        'stock.card.move', 'stock_card_product_id', 'Product Moves')

    @api.multi
    def stock_card_move_get(self):
        self.ensure_one()
        if not (self.product_id.valuation == 'real_time' and
                self.product_id.cost_method in ('average', 'real')):
            return True
        self.stock_card_move_ids.unlink()
        self._stock_card_move_get(self.product_id.id)

        return True

    def _get_quant_values(self, move_id, col='', inner='', where=''):
        self._cr.execute(
            '''
            SELECT
                COALESCE(cost, 0.0) AS cost,
                COALESCE(qty, 0.0) AS qty
                {col}
            FROM stock_quant_move_rel AS sqm_rel
            INNER JOIN stock_quant AS sq ON sq.id = sqm_rel.quant_id
            {inner}
            WHERE sqm_rel.move_id = {move_id}
            {where}
            '''.format(move_id=move_id, col=col, inner=inner, where=where)
        )
        return self._cr.dictfetchall()

    def _get_price_on_consumed(self, row, vals, qntval):
        move_id = row['move_id']
        # TODO: move to `transit` could be a return
        # average is kept unchanged products are taken at average price
        if not vals['move_dict'].get(move_id):
            vals['move_dict'][move_id] = {}
        vals['move_dict'][move_id]['average'] = vals['average']
        vals['move_valuation'] = sum(
            [vals['average'] * qnt['qty'] for qnt in qntval])
        # NOTE: For production
        # a) it could be a consumption: if so average is kept unchanged
        # products are taken at average price
        # TODO: Consider the case that
        # b) it could be a return: defective good, reworking, etc.
        return True

    def _get_price_on_supplier_return(self, row, vals, qntval):
        sm_obj = self.env['stock.move']
        move_id = row['move_id']
        move_brw = sm_obj.browse(move_id)
        # Cost is the one record in the stock_move, cost in the
        # quant record includes other segmentation cost: landed_cost,
        # material_cost, production_cost, subcontracting_cost
        # Inventory Value has to be decreased by the amount of purchase
        # TODO: BEWARE price_unit needs to be normalised
        vals['move_valuation'] = sum([move_brw.price_unit * qnt['qty']
                                      for qnt in qntval])
        return True

    def _get_price_on_supplied(self, row, vals, qntval):
        # TODO: transit could be a return that shall be recorded at
        # average cost of transaction
        # average is to be computed considering all the segmentation
        # costs inside quant
        vals['move_valuation'] = sum(
            [qnt['cost'] * qnt['qty'] for qnt in qntval])
        return True

    def _get_price_on_customer_return(self, row, vals, qntval):
        sm_obj = self.env['stock.move']
        move_id = row['move_id']
        move_brw = sm_obj.browse(move_id)
        # NOTE: Identify the originating move_id of returning move
        origin_id = move_brw.origin_returned_move_id.id
        # NOTE: Falling back to average in case customer return is
        # orphan, i.e., return was created from scratch
        old_average = (
            vals['move_dict'].get(origin_id, 0.0) and
            vals['move_dict'][move_id]['average'] or vals['average'])
        vals['move_valuation'] = sum(
            [old_average * qnt['qty'] for qnt in qntval])
        return True

    def _get_move_average(self, row, vals):
        qty = row['product_qty']
        vals['cost_unit'] = vals['move_valuation'] / qty if qty else 0.0

        vals['inventory_valuation'] += (
            vals['direction'] * vals['move_valuation'])

        vals['average'] = (
            vals['product_qty'] and
            vals['inventory_valuation'] / vals['product_qty'] or
            vals['average'])

    def _get_stock_card_move_line_dict(self, row, vals):
        res = dict(
            date=row['date'],
            move_id=row['move_id'],
            stock_card_product_id=self.id,
            product_qty=vals['product_qty'],
            qty=vals['direction'] * row['product_qty'],
            move_valuation=vals['direction'] * vals['move_valuation'],
            inventory_valuation=vals['inventory_valuation'],
            average=vals['average'],
            cost_unit=vals['cost_unit'],
        )
        return res

    def _get_stock_card_move_line(self, row, vals):
        res = self._get_stock_card_move_line_dict(row, vals)
        vals['lines'].append(res)
        return True

    def _get_average_by_move(self, product_id, row, vals, return_values=False):
        dst = row['dst_usage']
        src = row['src_usage']
        if dst == 'internal':
            vals['direction'] = 1
        else:
            vals['direction'] = -1

        vals['product_qty'] += (vals['direction'] * row['product_qty'])

        qntval = self._get_quant_values(row['move_id'])

        # TODO: What is to be done with `procurement` & `view`

        if dst in ('customer', 'production', 'inventory', 'transit'):
            self._get_price_on_consumed(row, vals, qntval)

        if dst in ('supplier',):
            self._get_price_on_supplier_return(row, vals, qntval)

        if src in ('supplier', 'production', 'inventory', 'transit'):
            self._get_price_on_supplied(row, vals, qntval)

        if src in ('customer',):
            self._get_price_on_customer_return(row, vals, qntval)

        self._get_move_average(row, vals)

        if not return_values:
            self._get_stock_card_move_line(row, vals)
        return True

    def _stock_card_move_get_avg(self, product_id, vals, return_values=False):
        for row in self._stock_card_move_history_get(product_id):
            self._get_average_by_move(
                product_id, row, vals, return_values=return_values)

        return vals

    def _get_default_params(self):
        return dict(
            product_qty=0.0,
            average=0.0,
            inventory_valuation=0.0,
            lines=[],
            move_dict={},
        )

    def _stock_card_move_get(self, product_id, return_values=False):
        scm_obj = self.env['stock.card.move']
        self.stock_card_move_ids.unlink()

        vals = self._get_default_params()

        res = self._stock_card_move_get_avg(
            product_id, vals, return_values=return_values)
        if return_values:
            return res
        for line in res.get('lines'):
            scm_obj.create(line)

        return True

    def get_average(self, product_id):
        res = self._stock_card_move_get(product_id, return_values=True)
        return res.get('average')

    def get_qty(self, product_id):
        res = self._stock_card_move_get(product_id, return_values=True)
        return res.get('product_qty')

    @api.multi
    def action_view_moves(self):
        '''
        This function returns an action that display existing invoices of given
        commission payment ids. It can either be a in a list or in a form view,
        if there is only one invoice to show.
        '''
        self.ensure_one()
        ctx = self._context.copy()

        ir_model_obj = self.pool['ir.model.data']
        model, action_id = ir_model_obj.get_object_reference(
            self._cr, self._uid, 'stock_card', 'stock_card_move_action')
        action = self.pool[model].read(
            self._cr, self._uid, action_id, context=self._context)
        action['context'] = ctx
        # compute the number of invoices to display
        scm_ids = [scm_brw.id for scm_brw in self.stock_card_move_ids]
        # choose the view_mode accordingly
        if len(scm_ids) >= 1:
            action['domain'] = "[('id','in',[" + ','.join(
                [str(scm_id) for scm_id in scm_ids]
            ) + "])]"
        else:
            action['domain'] = "[('id','in',[])]"
        return action

    def _stock_card_move_history_get(self, product_id):
        self._cr.execute(
            '''
            SELECT
                sm.id AS move_id, sm.date, sm.product_id, prod.product_tmpl_id,
                sm.product_qty, sl_src.usage AS src_usage,
                sl_dst.usage AS dst_usage,
                ir_prop_cost.value_text AS cost_method,
                sm.date AS date
            FROM stock_move AS sm
            INNER JOIN
                stock_location AS sl_src ON sm.location_id = sl_src.id
            INNER JOIN
                stock_location AS sl_dst ON sm.location_dest_id = sl_dst.id
            INNER JOIN
                 product_product AS prod ON sm.product_id = prod.id
            INNER JOIN
                product_template AS ptemp ON prod.product_tmpl_id = ptemp.id
            INNER JOIN
                ir_property AS ir_prop_cost ON (
                    ir_prop_cost.res_id = 'product.template,' ||
                    ptemp.id::text and ir_prop_cost.name = 'cost_method')
            WHERE
                sm.state = 'done' -- Stock Move already DONE
                AND ir_prop_cost.value_text = 'average' -- Average Products
                AND sl_src.usage != sl_dst.usage -- No self transfers
                AND (
                    (sl_src.usage = 'internal' AND sl_dst.usage != 'internal')
                    OR (
                    sl_src.usage != 'internal' AND sl_dst.usage = 'internal')
                ) -- Actual incoming or outgoing Stock Moves
                AND sm.product_id = %s
            ORDER BY sm.date
            ''', (product_id,)
        )
        return self._cr.dictfetchall()


class StockCardMove(models.TransientModel):
    _name = 'stock.card.move'

    stock_card_product_id = fields.Many2one(
        'stock.card.product', string='Stock Card Product')
    move_id = fields.Many2one('stock.move', string='Stock Moves')
    product_qty = fields.Float('Inventory Quantity')
    qty = fields.Float('Move Quantity')
    move_valuation = fields.Float(
        string='Move Valuation',
        digits=dp.get_precision('Account'),
        readonly=True)
    inventory_valuation = fields.Float(
        string='Inventory Valuation',
        digits=dp.get_precision('Account'),
        readonly=True)
    average = fields.Float(
        string='Average',
        digits=dp.get_precision('Account'),
        readonly=True)
    cost_unit = fields.Float(
        string='Unit Cost',
        digits=dp.get_precision('Account'),
        readonly=True)
    date = fields.Datetime(string='Date')
