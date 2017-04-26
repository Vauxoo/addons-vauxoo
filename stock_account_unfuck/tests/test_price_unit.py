# coding: utf-8

from openerp import fields
from openerp.tests.common import TransactionCase


class TestPriceUnit(TransactionCase):
    def setUp(self):
        super(TestPriceUnit, self).setUp()
        self.transfer_obj = self.env['stock.transfer_details']
        self.product_uom_unit = self.env.ref('product.product_uom_unit')
        self.supplier = self.env.ref('base.res_partner_1')
        self.supplier.property_product_pricelist.write(
            {'currency_id': self.env.ref('base.MXN').id})
        self.supplier.property_product_pricelist_purchase.write(
            {'currency_id': self.env.ref('base.MXN').id})
        self.env.user.company_id.write(
            {'currency_id': self.env.ref('base.MXN').id})
        self.customer = self.env.ref('base.res_partner_9')
        self.warehouse_1 = self.env.ref('stock_account_unfuck.whr_test_a')
        self.warehouse_2 = self.env.ref('stock_account_unfuck.whr_test_b')
        self.route_1 = self.env.ref(
            'stock_account_unfuck.stock_location_route_a')
        self.route_2 = self.env.ref(
            'stock_account_unfuck.stock_location_route_b')

    def create_product(self):

        dict_vals = {
            'name': 'Product test',
            'uom_id': self.product_uom_unit.id,
            'type': 'product',
            'cost_method': 'average',
            'valuation': 'real_time',
            'property_stock_account_input': self.env.ref('account.xfa').id,
            'property_stock_account_output': self.env.ref('account.stk').id,
        }
        product = self.env['product.product'].create(dict_vals)
        return product

    def create_purchase(self, supplier, product, warehouse, qty, price):
        purchase_vals_line = {
            'name': product.name,
            'product_id': product.id,
            'date_planned': fields.Date.today(),
            'product_qty': qty,
            'product_uom': product.uom_id.id,
            'price_unit': price,
        }
        purchase_vals = {
            'partner_id': self.supplier.id,
            'pricelist_id':
            self.supplier.property_product_pricelist_purchase.id,
            'location_id': warehouse.lot_stock_id.id,
            'picking_type_id': warehouse.in_type_id.id,
            'order_line': [
                (0, 0, purchase_vals_line)], }

        purchase = self.env['purchase.order'].create(purchase_vals)
        purchase.signal_workflow("purchase_confirm")
        purchase.signal_workflow("purchase_approve")
        return purchase

    def create_sale(self, customer, product, warehouse, qty, price,
                    route=False):
        sale_vals_line = {
            'name': product.name,
            'product_id': product.id,
            'product_uom_qty': qty,
            'product_uom': product.uom_id.id,
            'price_unit': price,
            'route_id': route and route.id,
        }

        sale_vals = {
            'partner_id': self.customer.id,
            'partner_invoice_id': self.customer.id,
            'partner_shipping_id': self.customer.id,
            'picking_policy': 'direct',
            'pricelist_id': self.ref('product.list0'),
            'warehouse_id': warehouse.id,
            'order_line': [
                (0, 0, sale_vals_line)], }

        sale_order = self.env['sale.order'].create(sale_vals)
        sale_order.action_button_confirm()
        return sale_order

    def transfer_picking(self, picking, product, qty, warehouse):
        if not picking.sale_id:
            self.env['stock.quant'].create({
                'location_id': picking.location_id.id,
                'product_id': product.id,
                'qty': qty,
            })

        if picking.state == 'confirmed':
            picking.action_assign()

        ctx = {
            "active_id": picking.id,
            "active_ids": [picking.id],
            "active_model": "stock.picking",
        }
        wizard_transfer_id = self.transfer_obj.with_context(ctx).create({
            'picking_id': picking.id, })
        wizard_transfer_id.with_context(
            warehouse=warehouse.id).do_detailed_transfer()

    def test_00_price_unit(self):
        """ Test changes in price_unit and average in products doing
        purchases and sales
        """
        product = self.create_product()
        supplierinfo = self.env['product.supplierinfo'].create({
            'name': self.supplier.id,
            'min_qty': 0.0,
            'delay': 1,
            'product_tmpl_id': product.product_tmpl_id.id})
        self.assertTrue(supplierinfo)

        # First purchase
        purchase_1 = self.create_purchase(
            self.supplier, product, self.warehouse_1, 100, 120)

        picking = purchase_1.picking_ids
        self.assertTrue(picking)

        self.transfer_picking(picking, product, 100, self.warehouse_1)
        self.assertEqual(picking.state, 'done')

        self.assertEqual(picking.move_lines[0].price_unit, 120)
        self.assertEqual(product.standard_price, 120)
        self.assertEqual(product.with_context(
            warehouse=self.warehouse_1.id).qty_available, 100)

        # Second purchase
        purchase_2 = self.create_purchase(
            self.supplier, product, self.warehouse_1, 10, 100)

        picking = purchase_2.picking_ids
        self.assertTrue(picking)

        self.transfer_picking(picking, product, 10, self.warehouse_1)
        self.assertEqual(picking.state, 'done')

        self.assertEqual(picking.move_lines[0].price_unit, 100)
        self.assertEqual(product.standard_price, 118.18)
        self.assertEqual(product.with_context(
            warehouse=self.warehouse_1.id).qty_available, 110)

        # First sale
        sale_1 = self.create_sale(
            self.customer, product, self.warehouse_1, 1, 100)
        picking = sale_1.picking_ids
        self.assertTrue(picking)

        self.transfer_picking(picking, product, 1, self.warehouse_1)
        self.assertEqual(picking.state, 'done')

        self.assertEqual(picking.move_lines[0].price_unit, 118.18)
        self.assertEqual(product.standard_price, 118.18)
        self.assertEqual(product.with_context(
            warehouse=self.warehouse_1.id).qty_available, 109)

        # Second sale
        sale_2 = self.create_sale(
            self.customer, product, self.warehouse_2, 1, 100, self.route_1)
        self.assertEqual(len(sale_2.picking_ids), 3)

        # First pick sale_2
        picking = sale_2.picking_ids.filtered(
            lambda pick: pick.state == 'confirmed')
        self.assertTrue(picking)

        self.transfer_picking(picking, product, 1, self.warehouse_1)
        self.assertEqual(picking.state, 'done')

        self.assertEqual(picking.move_lines[0].price_unit, 118.18)
        self.assertEqual(product.standard_price, 118.18)
        self.assertEqual(product.with_context(
            warehouse=self.warehouse_1.id).qty_available, 108)

        # Second pick sale_2
        picking = sale_2.picking_ids.filtered(
            lambda pick: pick.state == 'assigned')
        self.assertTrue(picking)

        self.transfer_picking(picking, product, 1, self.warehouse_2)
        self.assertEqual(picking.state, 'done')

        self.assertEqual(picking.move_lines[0].price_unit, 118.18)
        self.assertEqual(product.standard_price, 118.18)
        self.assertEqual(product.with_context(
            warehouse=self.warehouse_1.id).qty_available, 108)
        self.assertEqual(product.with_context(
            warehouse=self.warehouse_2.id).qty_available, 1)

        # Third pick sale_2
        picking = sale_2.picking_ids.filtered(
            lambda pick: pick.state == 'assigned')
        self.assertTrue(picking)

        self.transfer_picking(picking, product, 1, self.warehouse_1)
        self.assertEqual(picking.state, 'done')

        self.assertEqual(picking.move_lines[0].price_unit, 118.18)
        self.assertEqual(product.standard_price, 118.18)
        self.assertEqual(product.with_context(
            warehouse=self.warehouse_1.id).qty_available, 108)

        # Third sale
        sale_3 = self.create_sale(self.customer, product, self.warehouse_2, 1,
                                  100, self.route_2)
        self.assertEqual(len(sale_3.picking_ids), 3)

        purchase_from_sale = self.env['purchase.order'].search(
            [('partner_id', '=', self.supplier.id)], order='id desc', limit=1)
        self.assertTrue(purchase_from_sale)

        purchase_from_sale.order_line.write({'price_unit': 130})

        purchase_from_sale.signal_workflow("purchase_confirm")
        self.assertEqual(len(sale_3.picking_ids), 4)

        # First pick sale_3
        picking = sale_3.picking_ids.filtered(
            lambda pick: pick.state == 'assigned')
        self.assertTrue(picking)

        self.transfer_picking(picking, product, 1, self.warehouse_1)
        self.assertEqual(picking.state, 'done')

        self.assertEqual(picking.move_lines[0].price_unit, 130)
        self.assertEqual(product.standard_price, 118.29)
        self.assertEqual(product.with_context(
            warehouse=self.warehouse_1.id).qty_available, 109)

        # Second pick sale_3
        picking = sale_3.picking_ids.filtered(
            lambda pick: pick.state == 'assigned')
        self.assertTrue(picking)

        self.transfer_picking(picking, product, 1, self.warehouse_1)
        self.assertEqual(picking.state, 'done')

        self.assertEqual(picking.move_lines[0].price_unit, 118.29)
        self.assertEqual(product.standard_price, 118.29)
        self.assertEqual(product.with_context(
            warehouse=self.warehouse_1.id).qty_available, 108)

        # Third pick sale_3
        picking = sale_3.picking_ids.filtered(
            lambda pick: pick.state == 'assigned')
        self.assertTrue(picking)

        self.transfer_picking(picking, product, 1, self.warehouse_2)
        self.assertEqual(picking.state, 'done')

        self.assertEqual(picking.move_lines[0].price_unit, 118.29)
        self.assertEqual(product.standard_price, 118.29)
        self.assertEqual(product.with_context(
            warehouse=self.warehouse_1.id).qty_available, 108)
        self.assertEqual(product.with_context(
            warehouse=self.warehouse_2.id).qty_available, 1)

        # Fourth pick sale_3
        picking = sale_3.picking_ids.filtered(
            lambda pick: pick.state == 'assigned')
        self.assertTrue(picking)

        self.transfer_picking(picking, product, 1, self.warehouse_1)
        self.assertEqual(picking.state, 'done')

        self.assertEqual(picking.move_lines[0].price_unit, 118.29)
        self.assertEqual(product.standard_price, 118.29)
        self.assertEqual(product.with_context(
            warehouse=self.warehouse_1.id).qty_available, 108)
