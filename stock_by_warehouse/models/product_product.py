import json
from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp

UNIT = dp.get_precision('Product Unit of Measure')


class ProductProduct(models.Model):
    _inherit = "product.product"

    qty_available_not_res = fields.Float(
        string='Qty Available Not Reserved',
        digits=UNIT,
        compute='_compute_qty_available_not_reserved',
    )

    warehouses_stock = fields.Text(
        store=False, readonly=True,
    )

    warehouses_stock_recompute = fields.Boolean(store=False, readonly=False)

    @api.onchange('warehouses_stock_recompute')
    def _warehouses_stock_recompute_onchange(self):
        if not self.warehouses_stock_recompute:
            self.warehouses_stock_recompute = True
            return
        self.warehouses_stock = self._compute_get_quantity_warehouses_json()
        self.warehouses_stock_recompute = True

    @api.multi
    def _product_available_not_res_hook(self, quants):
        """Hook used to introduce possible variations"""
        return False

    @api.multi
    def _prepare_domain_available_not_reserved(self):
        domain_quant = [
            ('product_id', 'in', self.ids)
        ]
        domain_quant_locations = self._get_domain_locations()[0]
        domain_quant.extend(domain_quant_locations)
        return domain_quant

    @api.multi
    def _compute_qty_available_not_reserved(self):
        """Method to set the quantity available that is not reserved of a serie of products.
        """
        domain_quant = self._prepare_domain_available_not_reserved()
        quants = self.env['stock.quant'].with_context(lang=False).read_group(
            domain_quant, fields=['product_id', 'quantity', 'reserved_quantity'], groupby="product_id")

        res = {}
        for quant in quants:
            quantity = quant.get('quantity') - quant.get('reserved_quantity')
            res[quant.get('product_id')[0]] = max(quantity, 0.0)

        for prod in self:
            prod.qty_available_not_res = res.get(prod.id, 0.0)

    @api.multi
    def _compute_get_quantity_warehouses_json(self):
        # get original from onchange
        self_origin = self._origin if hasattr(self, '_origin') else self
        info = {'title': _('Stock by Warehouse'), 'content': [],
                'warehouse': self_origin.qty_available_not_res}
        if not self_origin.exists():
            return json.dumps(info)
        self_origin.ensure_one()

        # Just in case it's asked from other place different than product
        # itself, we enable this context management
        warehouse_id = self._context.get('warehouse_id')

        for warehouse in self.env['stock.warehouse'].sudo().search([]):
            product = self_origin.sudo().with_context(
                warehouse=warehouse.id, location=False)
            if warehouse_id and warehouse_id.id == warehouse.id:
                info['warehouse'] = product.qty_available_not_res
            info['content'].append({
                'warehouse': warehouse.name,
                'warehouse_short': warehouse.code,
                'product': product.id,
                'available_not_res': product.qty_available_not_res,
                'available': product.qty_available,
                'virtual': product.virtual_available,
                'incoming': product.incoming_qty,
                'outgoing': product.outgoing_qty,
                'saleable':
                product.qty_available - product.outgoing_qty
            })
        return json.dumps(info)
