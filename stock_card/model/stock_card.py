# coding: utf-8

from openerp import models, fields, api


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
        scm_obj = self.env['stock.card.move']
        self.stock_card_move_ids.unlink()
        product_qty = 0.0
        average = 0.0
        inventory_valuation = 0.0
        lines = []
        for row in self._stock_card_move_get():
            move_id = row['move_id']
            if row['dst_usage'] == 'internal':
                direction = 1
            else:
                direction = -1
            qty = direction * row['product_qty']
            product_qty += qty
            self._cr.execute(
                '''
                SELECT cost
                FROM stock_quant_move_rel AS sqm_rel
                INNER JOIN stock_quant AS sq ON sq.id = sqm_rel.quant_id
                WHERE sqm_rel.move_id = %s
                ''', (move_id,)
                )
            move_valuation = sum([val[0] for val in self._cr.fetchall()])
            cost_unit = move_valuation / qty  # TODO: Need to be changed
            inventory_valuation += direction * move_valuation
            average = inventory_valuation / product_qty
            lines.append(dict(
                date=row['date'],
                move_id=move_id,
                stock_card_product_id=self.id,
                product_qty=product_qty,
                qty=qty,
                move_valuation=move_valuation,
                inventory_valuation=inventory_valuation,
                average=average,
                cost_unit=cost_unit,
                ))
        for line in lines:
            scm_obj.create(line)

        return True

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

    @api.multi
    def _stock_card_move_get(self):
        self.ensure_one()
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
            ''', (self.product_id.id,)
        )
        return self._cr.dictfetchall()


class StockCardMove(models.TransientModel):
    _name = 'stock.card.move'

    stock_card_product_id = fields.Many2one(
        'stock.card.product', string='Stock Card Product')
    move_id = fields.Many2one('stock.move', string='Stock Moves')
    product_qty = fields.Float('Cumulative Quantity')
    qty = fields.Float('Move Quantity')
    move_valuation = fields.Float('Move Valuation')
    inventory_valuation = fields.Float('Inventory Valuation')
    average = fields.Float('Average')
    cost_unit = fields.Float('Unit Cost')
    date = fields.Datetime(string='Date')
