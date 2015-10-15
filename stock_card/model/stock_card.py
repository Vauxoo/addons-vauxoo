# coding: utf-8

from openerp import models, fields, api


class StockCard(models.TransientModel):
    _name = 'stock.card'
    product_ids = fields.Many2many('product.product', string='Products')


class StockCardProduct(models.TransientModel):
    _name = 'stock.card.product'
    product_id = fields.Many2one('product.product', string='Product')

    @api.multi
    def _stock_card_move_get(self):
        self.ensure_one()
        self._cr.execute(
            '''
            SELECT
                sm.id, sm.date, sm.product_id, prod.product_tmpl_id,
                sm.product_qty, sl_src.usage, sl_dst.usage,
                ir_prop_cost.value_text AS cost_method
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
        res = self._cr.dictfetchall()
        import pdb; pdb.set_trace()
        res = res  # Just to cheat on PYLINT, will be deleted
        return True


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
