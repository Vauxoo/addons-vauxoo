# -*- coding: utf-8 -*-

from openerp.addons.stock.tests.common import TestStockCommon


class TestsStockQuantCostSegmentation(TestStockCommon):

    """Testing Material Cost on Quants
    """

    def setUp(self):
        """basic method to define some basic data to be re use in all test cases.
        """
        super(TestsStockQuantCostSegmentation, self).setUp()
        self.quant = self.env['stock.quant']
        self.aml_obj = self.env['account.move.line']
        self.stock_inv_obj = self.env['stock.inventory']
        self.product_obj = self.env['product.product']
        self.product_id = self.ref(
            'stock_quant_cost_segmentation.product_real_realtime')
        self.inventory_id = self.stock_inv_obj.browse(self.ref(
            'stock_quant_cost_segmentation.stock_inventory_02'))
        self.product_sgmnt = self.product_obj.browse(self.ref(
            'stock_quant_cost_segmentation.product_sgmnt'))

    def asserting_cost_segmentation(self):
        quant = self.quant.search(
            [('product_id', '=', self.product_id)])

        self.assertEquals(
            (quant.cost, quant.material_cost),
            (100.0, 100.0),
            'Something went wrong. Material Cost value is 100.00!!!')

    def asserting_real_time_accounting(self):
        aml_ids = []
        for sm_brw in self.inventory_id.move_ids:
            aml_ids += self.aml_obj.search(
                [('sm_id', '=', sm_brw.id)])

        self.assertEquals(
            bool(aml_ids),
            True,
            'Something went wrong. There should be Journal Entries!!!')
        self.assertEquals(
            len(aml_ids),
            2,
            'Something went wrong. There should be Two Journal Entries!!!')

    def test_01_basic_landed(self):
        self.asserting_cost_segmentation()

    def test_02_basic_real_time_accouting(self):
        self.asserting_real_time_accounting()

    def test_03_segmentation_change_on_average(self):
        self.assertEquals(
            self.product_sgmnt.standard_price, 32,
            'Something went wrong. Standard Price value is 32.00!!!')
        self.assertEquals(
            self.product_sgmnt.material_cost, 32,
            'Something went wrong. Material Cost value is 32.00!!!')

    def test_04_quants_segmentation_initialization(self):
        self.quant.initializing_quant_segmentation()
        self.cr.execute(self.quant._sql_query_quants_not_fix)
        res = self.cr.fetchone()
        quants_qty = int(res[0])
        self.assertEquals(quants_qty, 0, "Quant haven't fixed")
