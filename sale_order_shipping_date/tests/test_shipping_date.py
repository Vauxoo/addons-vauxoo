# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
# #############Credits#########################################################
#    Coded by: Jose Suniaga <josemiguel@vauxoo.com>
###############################################################################
#    This program is free software: you can redistribute it and/or modify it
#    under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or (at your
#    option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#

###############################################################################
from dateutil.relativedelta import relativedelta
from openerp.addons.stock.tests.common import TestStockCommon
from openerp import _, fields


class TestSaleOrderShippingDate(TestStockCommon):

    def setUp(self):
        super(TestSaleOrderShippingDate, self).setUp()
        # TODO: Replace data demo with TestStockCommon data, for any reason
        # when try to implement: addons/stock/tests/test_resupply.py#L10-L33
        # quantity available for ProductA does not increase
        self.product = self.env.ref('product.product_product_29')
        self.bigwh = self.env.ref('stock.warehouse0')
        self.smallwh = self.env.ref('stock.stock_warehouse_shop0')
        self.smallwh.write({
            'default_resupply_wh_id': self.bigwh.id,
            'resupply_wh_ids': [(6, 0, [self.bigwh.id])],
        })

    def create_sale(self, product=None, warehouse=None, date_order=None):
        product = product or self.product
        sale = self.env['sale.order'].create({
            'order_policy': 'manual',
            'date_order': date_order or fields.Datetime.now(),
            'partner_id': self.partner_agrolite_id,
            'partner_invoice_id': self.partner_agrolite_id,
            'partner_shipping_id': self.partner_agrolite_id,
            'order_line': [(0, 0, {
                'name': product.name,
                'product_id': product.id,
                'product_uom_qty': 2,
                'product_uom': product.uom_id.id,
                'price_unit': product.list_price,
                'delay': 1,
            })],
            'pricelist_id': self.env.ref('product.list0').id,
            'warehouse_id': warehouse and warehouse.id or self.bigwh.id,
        })
        return sale

    def create_sale_order_line(self, sale, product):
        sale.write({'order_line': [(0, 0, {
            'name': product.name,
            'product_id': product.id,
            'product_uom_qty': 1,
            'product_uom': product.uom_id.id,
            'price_unit': product.list_price,
            'delay': 1,
        })]})

    def _create_picking_in(self, warehouse):
        picking = self.env['stock.picking']
        picking_values = {
            'picking_type_id': warehouse.in_type_id.id,
            'location_id': self.env.ref('stock.stock_location_suppliers').id,
            'location_dest_id': warehouse.lot_stock_id.id,
        }
        return picking.create(picking_values)

    def _create_move(self, product, src_loc, dst_loc, **values):
        stock_move = self.env['stock.move']
        # simulate create + onchange
        move = stock_move.new({
            'product_id': product.id,
            'location_id': src_loc,
            'location_dest_id': dst_loc,
        })
        move.onchange_product_id()
        move_values = move._convert_to_write(move._cache)
        move_values.update(**values)
        return stock_move.create(move_values)

    def _create_move_in(self, product=None, warehouse=None, picking=None,
                        create_picking=False, days_delay=0.0, **values):
        product = product or self.product
        warehouse = warehouse or self.bigwh
        if not values:
            move_dt = fields.Datetime.from_string(fields.Datetime.now()) + \
                relativedelta(days=days_delay)
            values = {
                'name': product.name,
                'company_id': self.env.ref('base.main_company').id,
                'product_uom': product.uom_id.id,
                'product_uom_qty': 5.0,
                'picking_type_id': warehouse.in_type_id.id,
                'warehouse_id': warehouse.id,
                'date': fields.Datetime.to_string(move_dt),
                'date_expected': fields.Datetime.to_string(move_dt),
            }
        if not picking and create_picking:
            picking = self._create_picking_in(warehouse)
        if picking:
            values['picking_id'] = picking.id
        src_loc = self.supplier_location
        dst_loc = warehouse.lot_stock_id.id
        return self._create_move(product, src_loc, dst_loc, **values)

    def test_compute_warehouse_date(self):
        product = self.env.ref('product.product_product_35')
        # create a incoming move for a product
        move = self._create_move_in(product=product, days_delay=2)
        move.action_confirm()
        right_date = fields.Datetime.from_string(move.date_expected)
        # create a demo Sale Order with a product not on hand but forecasted
        sale = self.create_sale()
        # compute date when product is available in warehouse
        warehouse_date = sale.order_line.compute_warehouse_date()
        self.assertEqual(warehouse_date, right_date)

    def test_compute_purchase_date(self):
        product = self.env.ref('product.product_product_35')
        sale = self.create_sale(product=product)
        # compute purchase date
        purchase_date = sale.order_line.compute_purchase_date()
        right_date = fields.Datetime.from_string(sale.date_order) + \
            relativedelta(days=product.seller_delay)
        self.assertEqual(purchase_date, right_date)

    def test_compute_manufacturing_date(self):
        product = self.env.ref('product.product_product_19')
        warehouse = self.env.ref('stock.warehouse0')
        sale = self.create_sale(product=product, warehouse=warehouse)
        # compute manufacturing date
        manufacturing_date = sale.order_line.compute_manufacturing_date()
        right_date = fields.Datetime.from_string(sale.date_order) + \
            relativedelta(days=product.produce_delay)
        self.assertEqual(manufacturing_date, right_date)

    def test_compute_resupply_date(self):
        product = self.env.ref('product.product_product_29')
        resupply_delay = 4.0
        resupply_route = self.env['stock.location.route'].search([
            ('supplied_wh_id', '=', self.smallwh.id)], limit=1)
        resupply_rule = resupply_route.pull_ids.filtered(
            lambda x: x.warehouse_id.id == self.smallwh.id)
        resupply_rule.write({'delay': resupply_delay})
        sale = self.create_sale(product=product, warehouse=self.smallwh)
        supplier_wh_date = sale.order_line.compute_warehouse_date(
            warehouse=self.bigwh)
        # compute resupply date
        resupply_date = sale.order_line.compute_resupply_date()
        right_date = supplier_wh_date + relativedelta(days=resupply_delay)
        self.assertEqual(resupply_date, right_date)

    def test_compute_shipping_date(self):
        """ Compute shipping date for order with 3 products

            by definition:
                shipping date, is the date by which the products are sure to
                be delivered. All products can be delivered the day when each
                one is available

            e.g.
            - products has 1 day delay
            - sale was created on 2016-10-25 20:57:49
            -------------------------------
            product Apple Wireless Keyboard
            warehouse Chicago Warehouse
            warehouse_date False
            resupply_date 2016-10-30 20:57:49 (day when each one is available)
            manuacturing_date False
            purchase_date 2016-10-29 20:57:49
            -------------------------------
            product Blank CD
            warehouse Chicago Warehouse
            warehouse_date False
            resupply_date False
            manuacturing_date False
            purchase_date 2016-10-27 20:57:49
            -------------------------------
            product USB Adapter
            warehouse Chicago Warehouse
            warehouse_date 2016-10-30 20:57:49
            resupply_date 2016-10-29 20:57:49
            manuacturing_date False
            purchase_date False
            -------------------------------

            at the end:
            - Apple Wireless Keyboard is the last product to get at stock
            - Apple Wireless Keyborad has 4 days PO delay + 1 day product delay
            - The shipping Date is 2016-10-30 20:57:49 (5 days after sale)
        """
        resupply_delay = 5.0
        product_delay = 1.0
        product_1 = self.env.ref('product.product_product_9')
        product_2 = self.env.ref('product.product_product_35')
        product_3 = self.env.ref('product.product_product_48')
        resupply_route = self.env['stock.location.route'].search([
            ('supplied_wh_id', '=', self.smallwh.id)], limit=1)
        resupply_rule = resupply_route.pull_ids.filtered(
            lambda x: x.warehouse_id.id == self.smallwh.id)
        resupply_rule.write({'delay': resupply_delay})
        sale = self.create_sale(product=product_1, warehouse=self.smallwh)
        self.create_sale_order_line(sale, product_2)
        self.create_sale_order_line(sale, product_3)
        sale._compute_shipping_date()
        shipping_date = fields.Datetime.from_string(sale.shipping_date)
        # according to example the shipping date for this case should be
        # 5 days after date order (product_1 seller delay + product delay)
        product_1_seller_delay = product_1.seller_ids[0].delay
        right_date = fields.Datetime.from_string(sale.date_order) + \
            relativedelta(days=(product_1_seller_delay + product_delay))
        self.assertEqual(shipping_date, right_date)
        # check onchange requested date
        res = sale.onchange_requested_date(
            sale.date_order, sale.shipping_date)
        self.assertIn('warning', res)
        msg = _("The date requested by the customer is "
                "sooner than the shipping date. You may be "
                "unable to honor the customer's request.")
        self.assertEqual(res['warning']['message'], msg)
