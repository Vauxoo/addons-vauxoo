# coding: utf-8

from openerp.tests.common import TransactionCase


class TestProductCustomerCodeCopy(TransactionCase):
    """Test for product_customer_code copy method.
    """

    # Method pseudo-constructor of test setUp
    def setUp(self):
        # Define global variables to test methods
        super(TestProductCustomerCodeCopy, self).setUp()
        self.product = self.env['product.product']

    def test_10_copy_method(self):
        """Test to verify that the copy method works fine
        """
        product = self.env.ref('product.product_product_1')
        product.copy()
