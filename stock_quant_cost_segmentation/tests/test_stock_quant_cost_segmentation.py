# -*- coding: utf-8 -*-

from openerp.addons.stock.tests.common import TestStockCommon


class TestsStockQuantCostSegmentation(TestStockCommon):

    """
    Testing Material Cost on Quants
    """

    def setUp(self):
        """
        basic method to define some basic data to be re use in all test cases.
        """
        super(TestsStockQuantCostSegmentation, self).setUp()
        self.quant = self.env['stock.quant']
        self.product_id = self.ref(
            'stock_quant_cost_segmentation.product_real_periodic')

    def asserting_cost_segmentation(self):
        quant = self.quant.search(
            [('product_id', '=', self.product_id)])

        self.assertEquals(
            (quant.cost, quant.material_cost),
            (100.0, 100.0),
            'Something went wrong. Material Cost value is 100.00!!!')
        return True

    def test_basic_landed(self):
        self.asserting_cost_segmentation()

        return True
