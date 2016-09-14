# coding: utf-8
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: Jose Suniaga <josemiguel@vauxoo.com>
#    planned by: Julio Serna <julio@vauxoo.com>
############################################################################

from openerp import api, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.multi
    def get_product_available_by_warehouse(self):
        ctx = dict(self._context)
        res = {}.fromkeys(self.ids, {})
        for product in self:
            qty_available = []
            virtual_available = []
            incoming_qty = []
            outgoing_qty = []
            for warehouse in self.env['stock.warehouse'].sudo().search([]):
                ctx.update({'warehouse': warehouse.id, 'location': False})
                product_qty = product.with_context(ctx).\
                    _product_available()[product.id]
                qty_available += [(warehouse, product_qty['qty_available'])]
                virtual_available += [
                    (warehouse, product_qty['virtual_available'])]
                incoming_qty += [(warehouse, product_qty['incoming_qty'])]
                outgoing_qty += [(warehouse, product_qty['outgoing_qty'])]
            res[product.id] = {
                'qty_available': qty_available,
                'virtual_available': virtual_available,
                'incoming_qty': incoming_qty,
                'outgoing_qty': outgoing_qty,
            }
        return res
