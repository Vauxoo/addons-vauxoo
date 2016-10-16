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
from openerp import _, api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    show_message = fields.Selection(
        selection=[
            ('qty_available', 'On hand quantity by warehouse'),
            ('virtual_available', 'Forecast quantity by warehouse'),
            ('incoming_qty', 'Incoming quantity by warehouse'),
            ('outgoing_qty', 'Outgoing quantity by warehouse'),
        ],
        string="Show Message",
        store=False,
        search=True)
        
    name = fields.Text(string='Description', required=True, size=2000)
        
    on_hand_ids = fields.One2many('warehouse.qty','on_hand_line_id',
                                    string='On hand quantity by warehouse',
                                    domain=[('name','=','qty_available')])
    forecast_ids = fields.One2many('warehouse.qty','forecast_line_id',
                                    string='Forecast quantity by warehouse',
                                    domain=[('name','=','virtual_available')])
    incoming_ids = fields.One2many('warehouse.qty','incoming_line_id',
                                    string='Incoming quantity by warehouse',
                                    domain=[('name','=','incoming_qty')])
    outgoing_ids = fields.One2many('warehouse.qty','outgoing_line_id',
                                    string='Outgoing quantity by warehouse',
                                    domain=[('name','=','outgoing_qty')])


    @api.multi
    def product_id_change_with_wh(
            self, pricelist, product, qty=0, uom=False, qty_uos=0, uos=False,
            name='', partner_id=False, lang=False, update_tax=True,
            date_order=False, packaging=False, fiscal_position=False,
            flag=False, warehouse_id=False):

        res = super(SaleOrderLine, self).product_id_change_with_wh(
            pricelist, product, qty, uom, qty_uos, uos, name, partner_id,
            lang, update_tax, date_order, packaging, fiscal_position, flag,
            warehouse_id)

        if not product:
            return res

        product_brw = self.env['product.product'].browse(product)
        titles = ['qty_available','virtual_available','incoming_qty',
                    'outgoing_qty']
        product_qty_by_wh = []
        route_ids = []
        on_hand_ids = []
        forecast_ids = []
        incoming_ids = []
        outgoing_ids = []
        
        for colname in titles:
            product_qty_by_wh = product_brw.\
                get_product_available_by_warehouse()[product][colname]
                
            for warehouse, product_qty in product_qty_by_wh:
                # TODO: uncomment until figure out a better way to choice only
                # the routes with availability
                # if product_qty > 0.0 and \
                #         colname in ['qty_available', 'virtual_available']:
                #     route_ids += [warehouse.delivery_route_id.id]
                dict_qty = (0,0,{'warehouse_id':warehouse.id,
                            'qty':product_qty,
                            'sale_order_line_id':self.id,
                            'name':colname})
                if colname == 'qty_available':
                    on_hand_ids.append(dict_qty)
                elif colname == 'virtual_available':
                    forecast_ids.append(dict_qty)
                elif colname == 'incoming_qty':
                    incoming_ids.append(dict_qty)
                elif colname == 'outgoing_qty':
                    outgoing_ids.append(dict_qty)

        res = {'value':{'on_hand_ids':on_hand_ids,
                        'forecast_ids':forecast_ids,
                        'incoming_ids':incoming_ids,
                        'outgoing_ids':outgoing_ids,
                        }}
        return res


class WarehouseQty(models.Model):
    _name = 'warehouse.qty'

    name = fields.Selection(
        selection=[
            ('qty_available', 'On hand quantity by warehouse'),
            ('virtual_available', 'Forecast quantity by warehouse'),
            ('incoming_qty', 'Incoming quantity by warehouse'),
            ('outgoing_qty', 'Outgoing quantity by warehouse'),
        ],
        string="Quantity by Warehouse",
        store=False,
        search=True)
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse')
    qty = fields.Float('Quantity')
    on_hand_line_id = fields.Many2one('sale.order.line' ,string='On Hand');
    forecast_line_id = fields.Many2one('sale.order.line' ,string='Forecast');
    incoming_line_id = fields.Many2one('sale.order.line' ,string='Incoming');
    outgoing_line_id = fields.Many2one('sale.order.line' ,string='Outgoing');
