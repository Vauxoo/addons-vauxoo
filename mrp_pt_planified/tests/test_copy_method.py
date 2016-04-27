# coding: utf-8

from openerp.tests.common import TransactionCase


class TestMrpProductsPlanifiedCopy(TransactionCase):
    """Test for mrp_pt_planified copy method.
    """

    # Method pseudo-constructor of test setUp
    def setUp(self):
        # Define global variables to test methods
        super(TestMrpProductsPlanifiedCopy, self).setUp()
        self.production = self.env['mrp.production']

    def test_10_copy_method(self):
        """Test to verify that the copy method works fine
        """
        production = self.env.ref('mrp.mrp_production_1')
        production.copy()
