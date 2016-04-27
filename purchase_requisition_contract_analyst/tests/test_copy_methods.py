# coding: utf-8

from openerp.tests.common import TransactionCase


class TestPurchaseRequisitionContractAnalystCopy(TransactionCase):
    """Test for purchase_requisition_contract_analyst copy method.
    """

    # Method pseudo-constructor of test setUp
    def setUp(self):
        # Define global variables to test methods
        super(TestPurchaseRequisitionContractAnalystCopy, self).setUp()
        self.requisition = self.env['purchase.requisition']

    def test_10_copy_method(self):
        """Test to verify that the copy method works fine
        """
        requisition = self.env.ref('purchase_requisition.requisition1')
        requisition.copy()
