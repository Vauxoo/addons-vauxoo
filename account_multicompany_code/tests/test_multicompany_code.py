from odoo.tests import TransactionCase


class TestMulticompanyCode(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.company = cls.env.ref("base.main_company")
        cls.company.code = "TEST-CODE"
        cls.account_type_expenses = cls.env.ref("account.data_account_type_expenses")

    def test_01_check_code_included_account_name(self):
        """Check that the code is shown in the account display names"""
        account = self.env["account.account"].create(
            {
                "name": "Account Name",
                "code": "999.01.05",
                "user_type_id": self.account_type_expenses.id,
                "company_id": self.company.id,
            }
        )
        expected_account_name = "999.01.05 Account Name (TEST-CODE)"
        self.assertEqual(account.display_name, expected_account_name)

    def test_02_check_code_included_journal_name(self):
        """Check that the code is shown in the account display names"""
        journal = self.env["account.journal"].create(
            {
                "name": "Journal Name",
                "code": "JTEST",
                "type": "general",
                "company_id": self.company.id,
            }
        )
        expected_journal_name = "Journal Name (TEST-CODE)"
        self.assertEqual(journal.display_name, expected_journal_name)
