from odoo.tests import TransactionCase


class TestMulticompanyCode(TransactionCase):
    def setUp(self):
        super().setUp()
        self.company = self.env.ref('base.main_company')
        self.company.code = 'TEST-CODE'

    def test_01_check_code_included_account_name(self):
        """Check that the code is shown in the account display names"""
        account = self.env['account.account'].search([
            ('company_id', '=', self.company.id),
            ('deprecated', '=', False),
            ], limit=1)
        expected_account_name = "%s %s (TEST-CODE)" % (account.code, account.name)
        self.assertEqual(account.display_name, expected_account_name)

    def test_02_check_code_included_journal_name(self):
        """Check that the code is shown in the account display names"""
        journal = self.env['account.journal'].search([
            ('company_id', '=', self.company.id),
            ('currency_id', '=', False),
            ], limit=1)
        expected_journal_name = "%s (TEST-CODE)" % journal.name
        self.assertEqual(journal.display_name, expected_journal_name)
