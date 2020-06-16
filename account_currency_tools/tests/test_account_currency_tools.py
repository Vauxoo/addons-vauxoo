from odoo.tests.common import TransactionCase


class TestsAccountCurrencyTools(TransactionCase):
    """ Testing all the features in Account Currency Tools """

    def setUp(self):
        """ Basic method to define some basic data to be re use in all test
        cases. """
        super(TestsAccountCurrencyTools, self).setUp()
        self.wzd_obj = self.env['foreign.exchange.realization']
        self.rc_obj = self.env['res.company']
        self.company_id = self.ref('base.main_company')

    def create_wizard(self, default=None):
        default = dict(default or {})
        values = dict(
            root_id=self.ref('account.chart0'),
            fiscalyear_id=self.ref('account.data_fiscalyear'),
            target_move='all',
            journal_id=self.ref('account.miscellaneous_journal'),
            period_id=self.ref('account.period_12'),
            company_id=self.company_id,
        )
        values.update(default)

        return self.wzd_obj.create(values)

    def test_basic_report(self):
        wzd_brw = self.create_wizard()

        wzd_brw.action_prepare()
        self.assertFalse(wzd_brw.skip_close_fiscalyear)

        wzd_brw.skip_close_fiscalyear = True
        wzd_brw.action_prepare()

        self.assertFalse(wzd_brw.skip_opening_entry)
        wzd_brw.skip_opening_entry = True
        wzd_brw.action_prepare()

        wzd_brw.action_progress()
        wzd_brw.income_currency_exchange_account_id = self.ref(
            'account.income_fx_income')
        wzd_brw.expense_currency_exchange_account_id = self.ref(
            'account.income_fx_expense')
        wzd_brw.action_create_move()
        self.assertTrue(bool(wzd_brw.move_id), 'No Journal Entry created')
        return True

    def test_exception_state(self):
        wzd_brw = self.create_wizard({'target_move': 'posted'})

        wzd_brw.action_prepare()
        wzd_brw.skip_close_fiscalyear = True
        wzd_brw.action_prepare()
        wzd_brw.skip_opening_entry = True
        wzd_brw.action_prepare()
        wzd_brw.action_progress()
        wzd_brw.income_currency_exchange_account_id = self.ref(
            'account.income_fx_income')
        wzd_brw.expense_currency_exchange_account_id = self.ref(
            'account.income_fx_expense')
        wzd_brw.action_create_move()
        self.assertEqual(wzd_brw.state, 'exception', 'No intended state')
        return True

    def test_non_multicurrency_accounts(self):
        rc_brw = self.rc_obj.browse(self.company_id)
        rc_brw.check_non_multicurrency_account = True

        wzd_brw = self.create_wizard()
        self.assertTrue(wzd_brw.check_non_multicurrency_account,
                        'Expected to Check Non Multicurrency Accounts')

        wzd_brw.action_prepare()
        wzd_brw.skip_close_fiscalyear = True
        wzd_brw.action_prepare()
        wzd_brw.skip_opening_entry = True
        wzd_brw.action_prepare()
        wzd_brw.action_progress()
        wzd_brw.income_currency_exchange_account_id = self.ref(
            'account.income_fx_income')
        wzd_brw.expense_currency_exchange_account_id = self.ref(
            'account.income_fx_expense')
        wzd_brw.action_create_move()
        self.assertEqual(wzd_brw.state, 'posted', 'No intended state')
        return True

    def test_redirect_gain_loss(self):
        wzd_brw = self.create_wizard()
        wzd_brw.action_prepare()
        wzd_brw.skip_close_fiscalyear = True
        wzd_brw.action_prepare()
        wzd_brw.skip_opening_entry = True
        wzd_brw.action_prepare()
        wzd_brw.bank_gain_exchange_account_id = self.ref(
            'account.income_fx_income')
        wzd_brw.bank_loss_exchange_account_id = self.ref(
            'account.income_fx_expense')
        wzd_brw.action_progress()
        wzd_brw.income_currency_exchange_account_id = self.ref(
            'account.income_fx_income')
        wzd_brw.expense_currency_exchange_account_id = self.ref(
            'account.income_fx_expense')
        wzd_brw.action_create_move()
        self.assertEqual(wzd_brw.state, 'posted', 'No intended state')
        return True
