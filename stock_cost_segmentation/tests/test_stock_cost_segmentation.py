# -*- coding: utf-8 -*-

from odoo.addons.stock.tests.common import TestStockCommon


class TestsStockmoveCostSegmentation(TestStockCommon):

    """Testing Material Cost on moves
    """

    def setUp(self):
        """basic method to define some basic data to be re use in all test cases.
        """
        super(TestsStockmoveCostSegmentation, self).setUp()
        self.move = self.env['stock.move']
        self.sale = self.env['sale.order']
        self.aml_obj = self.env['account.move.line']
        self.stock_inv_obj = self.env['stock.inventory']
        self.product_obj = self.env['product.product']
        self.product_id = self.env.ref(
            'stock_cost_segmentation.product_real_realtime')
        self.inventory_id = self.env.ref(
            'stock_cost_segmentation.stock_inventory_02')
        # Validating Documents
        self.product_sgmnt = self.env.ref(
            'stock_cost_segmentation.product_sgmnt')
        purchase = self.env.ref('stock_cost_segmentation.po_sgmnt_01')
        purchase.button_confirm()
        wizard = self.env['stock.immediate.transfer'].create(
            {'pick_ids': [(6, 0, purchase.picking_ids.ids)]})
        wizard.process()
        inventories = (
            self.env.ref('stock_cost_segmentation.stock_inventory_01') +
            self.env.ref('stock_cost_segmentation.stock_inventory_02'))
        inventories.action_start()
        inventories.action_validate()

    def asserting_cost_segmentation(self):
        move = self.move.search(
            [('product_id', '=', self.product_id.id),
             ('price_unit', '>', 1)])

        self.assertEquals(
            (move.price_unit, move.material_cost),
            (100.0, 100.0),
            'Something went wrong. Material Cost value should be 100.00!!!')

    def asserting_real_time_accounting(self):
        aml_ids = []
        for sm_brw in self.inventory_id.move_ids:
            aml_ids += self.aml_obj.search(
                [('move_id.stock_move_id', '=', sm_brw.id)])

        self.assertEquals(
            bool(aml_ids),
            True,
            'Something went wrong. There should be Journal Entries!!!')
        self.assertEquals(
            len(aml_ids),
            2,
            'Something went wrong. There should be Two Journal Entries!!!')

    def get_out(self, product):
        """Generating a sale order to move out the product and update its
        cost(FIFO)"""
        sale = self.sale.create(
            {'client_order_ref': 'ref1',
             'name': 'Test_SO001',
             'partner_id': self.env.ref('base.res_partner_4').id,
             'partner_invoice_id':
             self.env.ref('base.res_partner_address_7').id,
             'partner_shipping_id':
             self.env.ref('base.res_partner_address_7').id,
             'picking_policy': 'direct',
             'pricelist_id': self.env.ref('product.list0').id,
             'order_line': [
                 (0, 0,
                  {'product_id': product.id,
                   'price_unit': 50,
                   'name': product.name,
                   'product_uom_qty': 1,
                   'product_uom': self.env.ref('uom.product_uom_unit').id,
                   })]})

        sale.action_confirm()
        wizard = self.env['stock.immediate.transfer'].create(
            {'pick_ids': [(6, 0, sale.picking_ids.ids)]})
        wizard.process()

    def test_01_basic_landed(self):
        self.asserting_cost_segmentation()

    def test_02_basic_real_time_accouting(self):
        self.asserting_real_time_accounting()

    def test_03_segmentation_change_on_average(self):
        self.assertNotEquals(
            self.product_sgmnt.standard_price, 32,
            'Something went wrong. Standard Price value is 32.00!!!')
        self.assertNotEquals(
            self.product_sgmnt.material_cost, 32,
            'Something went wrong. Material Cost value is 32.00!!!')
        # Moving out products
        self.get_out(self.product_sgmnt)
        self.assertEquals(
            self.product_sgmnt.standard_price, 32,
            'Something went wrong. Standard Price value is 32.00!!!')
        self.assertEquals(
            self.product_sgmnt.material_cost, 32,
            'Something went wrong. Material Cost value is 32.00!!!')

    def test_04_check_move_history(self):
        """Checking if the moves have the right history"""
        self.get_out(self.product_sgmnt)
        sale = self.env['sale.order'].search(
            [('order_line.product_id', '=', self.product_sgmnt.id)])
        move = sale.picking_ids.move_lines
        self.assertEquals(
            move.move_orig_financial_ids.cost, 32,
            'The history is wrong')
        self.assertEquals(
            move.move_orig_logistic_ids.cost, 32,
            'The history is wrong')
        purchase = self.env.ref('stock_cost_segmentation.po_sgmnt_01')
        move_in = purchase.picking_ids.move_lines
        self.assertEquals(
            move_in, move.move_orig_logistic_ids.origin_move_id,
            'The history is wrong')
