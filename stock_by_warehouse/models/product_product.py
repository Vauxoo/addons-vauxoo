import json
from collections import defaultdict
from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.tools import float_is_zero

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

    warehouses_stock_location = fields.Text(store=False, readonly=True)

    warehouses_stock_recompute = fields.Boolean(store=False)

    @api.onchange('warehouses_stock_recompute')
    def _warehouses_stock_recompute_onchange(self):
        if not self.warehouses_stock_recompute:
            self.warehouses_stock_recompute = True
            return
        self.warehouses_stock = self._compute_get_quantity_warehouses_json()
        self.warehouses_stock_location = self._compute_get_stock_location()
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

    @api.multi
    def _compute_get_stock_location(self):
        """Method to get the stock quants that have a specific product and the locations of all the warehouses.
        It will return a dict with the location and quantity, the location with the most quantity of the product,
        and a number of locations where the product is available.
        """

        # Get original from onchange
        self_origin = getattr(self, '_origin', self)
        info = {'title': _('Stock by Warehouse and Locations'), 'content': []}
        if not self_origin.exists():
            return json.dumps(info)

        # To avoid that multiple records call this method when is called from another method other than an onchange
        self.ensure_one()

        # Just in case it's asked from other place different than product
        # itself, we enable this context management
        warehouse_context = self._context.get('warehouse')

        warehouses = warehouse_context and warehouse_context or self.env['stock.warehouse'].sudo().search([])
        available_locations_warehouse = 0
        for warehouse in warehouses:
            # Get all the stock locations that are part of the warehouse.
            warehouse_locations = self.env['stock.location'].sudo().search([
                ('id', 'child_of', warehouse.lot_stock_id.id), ('usage', '=', 'internal')])

            quants = self.env['stock.quant'].sudo().search([
                ('product_id', '=', self_origin.id), ('location_id', 'in', warehouse_locations.ids),
                ('quantity', '>', 0)])

            if not quants:
                continue

            most_quantity_location = False
            info_content = []
            qty_per_location_dict = defaultdict(float)
            for quant in quants:
                # Get the real quantity of product that is available, excluding reserved products.
                quantity = quant.quantity - quant.reserved_quantity
                if not float_is_zero(quantity, precision_rounding=self.uom_id.rounding):
                    qty_per_location_dict[quant.location_id] += quantity

            locations_available = len(qty_per_location_dict)
            available_locations_warehouse += len(qty_per_location_dict)

            qty_per_location = [(quantity, location) for location, quantity in qty_per_location_dict.items()]
            # This sort the list by the first element by default, in reverse mode because we want the locations with
            # the most quantity at first places.
            qty_per_location.sort(reverse=True)

            if qty_per_location:
                # Get the location with most quantities of products available.
                most_quantity_location = qty_per_location[0][1]

            info_content += [
                {'location': location.display_name, 'quantity': quantity} for quantity, location in qty_per_location]
            info['content'].append({
                'warehouse_name': warehouse.name,
                'most_quantity_location_id': most_quantity_location.id,
                'info_content': info_content,
                'locations_available': locations_available
            })

        info['available_locations'] = available_locations_warehouse
        return json.dumps(info)
