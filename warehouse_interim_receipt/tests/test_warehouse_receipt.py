# -*- coding: utf-8 -*-
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: Katherine Zaoral <kathy@vauxoo.com>
#    planned by: Rafael Silva <rsilvam@vauxoo.com>
############################################################################

from openerp.tests import common
from openerp.exceptions import ValidationError
import time
import random


class TestWarehouseReceipt(common.TransactionCase):

    def setUp(self):
        super(TestWarehouseReceipt, self).setUp()
        self.picking_obj = self.env['stock.picking']
        self.move_obj = self.env['stock.move']
        self.whr_obj = self.env['warehouse.receipt']
        self.purchase_obj = self.env['purchase.order']
        self.wiz_obj = self.env['wizard.modify.warehouse.receipt']
        self.wiz2_obj = self.env['wizard.warehouse.receipt.input']
        self.product_obj = self.env['product.product']
        self.product = self.product_obj.browse(
            self.ref('product.product_product_7'))

    def create_move(self, picking=False):
        """ Utility to create moves during the test.
        """
        values = {
            'name': 'SMTN Test Move',
            'picking_type_id': self.ref('stock.picking_type_in'),
            'product_id': self.ref('product.product_product_4'),
            'product_uom': self.ref('product.product_uom_unit'),
            'product_uom_qty': 500,
            'location_id': self.ref('stock.stock_location_suppliers'),
            'location_dest_id': self.ref('stock.stock_location_stock'), }
        if picking:
            values.update(picking_id=picking.id)
        move = self.move_obj.create(values)
        return move

    def create_picking(self):
        """ Utility to create pickings during the test.
        """
        values = {
            'origin': 'SMTN Picking Test',
            'picking_type_id': self.ref('stock.picking_type_in'),
            'partner_id': self.ref('base.res_partner_3'),
        }
        picking = self.picking_obj.create(values)
        self.assertTrue(picking)
        return picking

    def test_01(self):
        """Basic CRUD stock move
        """
        # Create
        move = self.create_move()
        self.assertEqual(move.state, 'draft')

        # Read (via ORM)
        move.read([])

        # Read (via direct)
        self.assertTrue(move.name)
        self.assertFalse(move.warehouse_receipt_id)

        # Write
        move.name = 'new name'
        self.assertEqual(move.name, 'new name')

        # Copy
        move2 = move.copy()
        self.assertTrue(move2)

        # Delete
        self.assertTrue(move.exists())
        move.unlink()
        self.assertFalse(move.exists())

    def test_02(self):
        """Basic CRUD warehouse receipt
        """
        # Create
        code = 'INTERIM-COD-1234'
        whr = self.whr_obj.create({'code': code})
        self.assertTrue(whr)

        # Read (via ORM)
        whr.read([])

        # Read (via direct). Check default value for sequence assignation
        self.assertEqual(whr.sequence, 10)
        self.assertEqual(whr.code, code)

        # Write
        new_code = ' '.join(['NEW:', code])
        whr.code = new_code
        self.assertEqual(whr.code, new_code)

        # Copy
        whr2 = whr.copy({'code': 'REQUIRED NEW CODE'})
        self.assertTrue(whr2)

        # Delete
        self.assertTrue(whr.exists())
        whr.unlink()
        self.assertFalse(whr.exists())

    def test_03(self):
        """ Modify Warehouse Receipt Wizard
        """
        # Create a stock picking with multiple move lines
        picking = self.create_picking()
        move1 = self.create_move(picking=picking)
        move2 = self.create_move(picking=picking)

        # Check that all the move lines are not done
        self.assertEqual(move1.state, 'draft')
        self.assertEqual(move2.state, 'draft')

        # Check that all the move lines have empty Warehouse Receipt
        self.assertFalse(move1.warehouse_receipt_id)
        self.assertFalse(move2.warehouse_receipt_id)

        # Run wizard (simulate run from picking form view).
        new_warehouse_receipt = self.whr_obj.create({'code': '123456'})
        self.assertTrue(new_warehouse_receipt)
        wiz = self.wiz_obj.with_context({
            'active_model': 'stock.picking',
            'active_id': picking.id,
            'active_ids': [picking.id],
        }).create({'warehouse_receipt_id': new_warehouse_receipt.id})
        self.assertTrue(wiz)
        self.assertTrue(wiz.lines)
        wiz.modify()

        # Check that all the move line were set with the Warehouse Receipt.
        self.assertEqual(move1.warehouse_receipt_id, new_warehouse_receipt)
        self.assertEqual(move2.warehouse_receipt_id, new_warehouse_receipt)

    def create_po_and_validate(self):
        """ Create a purchase order """
        pricelist_id = 1
        partner_id = self.ref('base.res_partner_1')
        order = self.purchase_obj.create({
            'partner_id': partner_id,
            'location_id': self.ref('stock.stock_location_stock'),
            'pricelist_id': pricelist_id})
        self.assertTrue(order)

        # create purchase order lines
        for item in range(3):
            self.create_pol(order, self.product)

        order.signal_workflow('purchase_confirm')
        self.assertEqual(order.state, 'approved')
        order.picking_ids.do_transfer()

        return order

    def create_pol(self, order, product):
        """
        Create a new purchase order line for the given purchase order taking
        as input only the product
        """
        write_flag = order.write({
            'order_line': [(0, 0, {
                'product_id': product.id,
                'product_qty': random.random()*1000,
                'product_uom': product.uom_id.id,
                'price_unit': product.price,
                'name': product.name_template,
                'date_planned': time.strftime('%Y-%m-%d')
            })]})
        self.assertTrue(write_flag)

    def test_04(self):
        """ Wizard Warehouse Receipt Input
        """
        # Create a stock picking with multiple move lines
        whr = self.whr_obj.create({'code': '123456'})
        self.assertTrue(whr)
        purchase_orders = self.purchase_obj
        for num in range(4):
            order = self.create_po_and_validate()
            for move in order.picking_ids.mapped('move_lines'):
                move.warehouse_receipt = whr
            purchase_orders = purchase_orders | order

        # Run wizard (simulate run from picking form view).
        wiz = self.wiz2_obj.create({
            'name': 'Current Week',
            'bol': 'CONT0001',
            'purchase_order_ids': purchase_orders.mapped('id'),
        })
        self.assertTrue(wiz)

    def test_05(self):
        """ Unique Warehouse Receipt Code
        """
        code = 'INTERIM-COD-1234'
        whr = self.whr_obj.create({'code': code})
        self.assertTrue(whr)

        msg = 'The warehouse receipt code must be unique'
        with self.assertRaisesRegexp(ValidationError, msg):
            self.whr_obj.create({'code': code})
