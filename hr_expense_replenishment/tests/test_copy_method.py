# coding: utf-8

from openerp.tests.common import TransactionCase


class TestHrExpenseReplenishmentCopy(TransactionCase):
    """Test for hr_expense_replenishment copy methods.
    """

    # Method pseudo-constructor of test setUp
    def setUp(self):
        # Define global variables to test methods
        super(TestHrExpenseReplenishmentCopy, self).setUp()
        self.expense = self.env['hr.expense.expense']
        self.invoice = self.env['account.invoice']

    def test_10_copy_method(self):
        """Test to verify that the copy methods works fine
        """
        expense = self.env.ref('hr_expense.expenses0')
        expense.copy()
        invoice = self.env.ref('account.invoice_2')
        invoice.copy()
