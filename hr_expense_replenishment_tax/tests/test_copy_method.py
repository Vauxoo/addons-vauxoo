# coding: utf-8

from openerp.tests.common import TransactionCase


class TestHrExpenseReplenishmentTaxCopy(TransactionCase):
    """Test for hr_expense_replenishment_tax copy method.
    """

    # Method pseudo-constructor of test setUp
    def setUp(self):
        # Define global variables to test methods
        super(TestHrExpenseReplenishmentTaxCopy, self).setUp()
        self.expense = self.env['hr.expense.expense']

    def test_10_copy_method(self):
        """Test to verify that the copy method works fine
        """
        expense = self.env.ref('hr_expense.expenses0')
        expense.copy()
