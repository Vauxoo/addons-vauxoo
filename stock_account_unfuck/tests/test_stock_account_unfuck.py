# -*- coding: utf-8 -*-

from openerp.tests.common import TransactionCase


class TestStockCard(TransactionCase):

    def setUp(self):
        super(TestStockCard, self).setUp()
        self.aml_obj = self.env['account.move.line']
        self.product_id = self.env.ref(
            'stock_account_unfuck.product_01_victrola')

    def test_00_logistic_test(self):
        """ Testing Logistic Values on VX Victrola."""
        self.assertEqual(
            self.product_id.standard_price, 383.33,
            "Expected Average - Cost Price is 383.33")

        self.assertEqual(
            self.product_id.qty_available, 0,
            "All merchandise should have been depleted")

    def test_01_accounting_test(self):
        """ Testing Accounting Valuation on VX Victrola."""
        val_id = self.product_id.categ_id.property_stock_valuation_account_id
        aml_ids = self.aml_obj.search(
            [('product_id', '=', self.product_id.id),
             ('account_id', '=', val_id.id)])
        debit = sum([aml.debit for aml in aml_ids])
        credit = sum([aml.credit for aml in aml_ids])
        self.assertEqual(debit, 4300.0, "Expected Debit: 4300.0")
        self.assertEqual(credit, 4299.99, "Expected Debit: 4299.99")
