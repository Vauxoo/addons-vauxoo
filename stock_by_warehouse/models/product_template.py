import json
from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp

UNIT = dp.get_precision('Product Unit of Measure')


class ProductTemplate(models.Model):
    _inherit = "product.template"

    qty_available_not_res = fields.Float(
        string='Quantity On Hand Unreserved',
        digits=UNIT,
        compute='_compute_product_available_not_res',
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
    @api.depends('product_variant_ids.qty_available_not_res')
    def _compute_product_available_not_res(self):
        for tmpl in self:
            if isinstance(tmpl.id, models.NewId):
                continue
            tmpl.qty_available_not_res = sum(
                tmpl.mapped('product_variant_ids.qty_available_not_res')
            )

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
            tmpl = self_origin.sudo().with_context(
                warehouse=warehouse.id, location=False)
            if warehouse_id and warehouse_id.id == warehouse.id:
                info['warehouse'] = tmpl.qty_available_not_res
            info['content'].append({
                'warehouse': warehouse.name,
                'warehouse_short': warehouse.code,
                'product': tmpl.id,
                'available_not_res': tmpl.qty_available_not_res,
                'available': tmpl.qty_available,
                'virtual': tmpl.virtual_available,
                'incoming': tmpl.incoming_qty,
                'outgoing': tmpl.outgoing_qty,
                'saleable':
                tmpl.qty_available - tmpl.outgoing_qty
            })
        return json.dumps(info)
