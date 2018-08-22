# coding: utf-8


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
        compute='_compute_get_quantity_warehouses_json'
    )

    @api.multi
    @api.depends('product_variant_ids.qty_available_not_res')
    def _compute_product_available_not_res(self):
        for tmpl in self:
            if isinstance(tmpl.id, models.NewId):
                continue
            tmpl.qty_available_not_res = sum(
                tmpl.mapped('product_variant_ids.qty_available_not_res')
            )

    @api.one
    @api.depends('product_variant_ids.warehouses_stock')
    def _compute_get_quantity_warehouses_json(self):
        info = {'title': _('Stock by Warehouse'), 'content': [],
                'warehouse': self.qty_available_not_res}

        # Just in case it's asked from other place different than product
        # itself, we enable this context management
        warehouse_id = self._context.get('warehouse_id')

        for warehouse in self.env['stock.warehouse'].sudo().search([]):
            tmpl = self.sudo().with_context(
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
        self.warehouses_stock = json.dumps(info)


class ProductProduct(models.Model):
    _inherit = "product.product"

    qty_available_not_res = fields.Float(
        string='Qty Available Not Reserved',
        digits=UNIT,
        compute='_compute_qty_available_not_reserved',
    )

    warehouses_stock = fields.Text(
        compute='_compute_get_quantity_warehouses_json')

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
    def _compute_product_available_not_res_dict(self):

        res = {}

        domain_quant = self._prepare_domain_available_not_reserved()
        quants = self.env['stock.quant'].with_context(lang=False).search(
            domain_quant,
        ).filtered(lambda x: x.reserved_quantity < x.quantity)
        # TODO: this should probably be refactored performance-wise
        for prod in self:
            vals = {}
            prod_quant = quants.filtered(lambda x: x.product_id == prod)
            quantity = sum(prod_quant.mapped(
                lambda x: x._get_available_quantity(
                    x.product_id,
                    x.location_id
                )
            ))
            vals['qty_available_not_res'] = quantity
            res[prod.id] = vals
        self._product_available_not_res_hook(quants)

        return res

    @api.multi
    def _compute_qty_available_not_reserved(self):
        res = self._compute_product_available_not_res_dict()
        for prod in self:
            qty = res[prod.id]['qty_available_not_res']
            prod.qty_available_not_res = qty
        return res

    @api.one
    @api.depends('stock_quant_ids', 'stock_move_ids')
    def _compute_get_quantity_warehouses_json(self):
        info = {'title': _('Stock by Warehouse'), 'content': [],
                'warehouse': self.qty_available_not_res}

        # Just in case it's asked from other place different than product
        # itself, we enable this context management
        warehouse_id = self._context.get('warehouse_id')

        for warehouse in self.env['stock.warehouse'].sudo().search([]):
            product = self.sudo().with_context(
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
        self.warehouses_stock = json.dumps(info)
