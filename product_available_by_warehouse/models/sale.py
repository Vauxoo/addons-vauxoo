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

    @api.multi
    def onchange_show_message(self, show_message, product_id):
        if not (show_message and product_id):
            return {}

        colname = show_message
        product = self.env['product.product'].browse(product_id)
        titles = {
            'qty_available': _('Product available by Warehouse'),
            'virtual_available': _('Forecast Quantity by Warehouse'),
            'incoming_qty': _('Incoming Quantity by Warehouse'),
            'outgoing_qty': _('Outgoing Quantity by Warehouse'),
        }
        warning_msgs = "%s\n\n" % product.name
        product_qty_by_wh = []
        route_ids = []
        if colname in titles:
            ctx = ((colname == 'qty_available') and
                   {'qty_available': True} or {})
            product_qty_by_wh = product.with_context(ctx).\
                get_product_available_by_warehouse()[product.id][colname]
        for warehouse, product_qty in product_qty_by_wh:
            # TODO: uncomment until figure out a better way to choice only
            # the routes with availability
            # if product_qty > 0.0 and \
            #         colname in ['qty_available', 'virtual_available']:
            #     route_ids += [warehouse.delivery_route_id.id]
            warning_msgs += _("- %s . Quantity: %.2f \n" %
                              (warehouse.name, product_qty))
        res = {}
        # update of warning messages
        if product_qty_by_wh:
            warning = {
                'title': titles[colname],
                'message': warning_msgs,
            }
            res.update({'warning': warning})

        # update route domain
        if route_ids:
            domain = res.get('domain', {})
            domain['route_id'] = [('id', 'in', route_ids)]
            res.update({'domain': domain})
        return res

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

        if self._context.get('show_message'):
            colname = self._context.get('show_message')

            result = self.onchange_show_message(colname, product)
            # replace warning
            if 'warning' in result:
                res.update({'warning': result['warning']})
            # update domain
            if 'domain' in result:
                domain = res.get('domain', {})
                domain['route_id'] = result['domain'].get('route_id', [])
                res.update({'domain': domain})
        return res
