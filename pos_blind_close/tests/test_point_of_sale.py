# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import odoo.tests

@odoo.tests.tagged('post_install', '-at_install')
class TestFrontend(odoo.tests.HttpCase):
    def setUp(self):
        super().setUp()
        self.main_user = self.env.ref('base.user_admin')
        self.env = self.env(user=self.main_user)
        self.pos_config = self.env['pos.config'].create({
            'name': 'Bar',
            'hide_totals_at_closing_session': True,
            'pricelist_id': self.env.ref('product.list0').id,
        })
        main_company = self.env.ref('base.main_company')
        test_sale_journal = self.env['account.journal'].create({
            'name': 'Sales Journal - Test',
            'code': 'TSJ',
            'type': 'sale',
            'company_id': main_company.id
        })
        cash_journal = self.env['account.journal'].create({
            'name': 'Cash Test',
            'code': 'TCJ',
            'type': 'cash',
            'company_id': main_company.id
        })
        account_receivable = self.env['account.account'].create({
            'code': 'X1012',
            'name': 'Account Receivable - Test',
            'user_type_id': self.env.ref('account.data_account_type_receivable').id,
            'reconcile': True,
        })
        self.pos_config.write({
            'journal_id': test_sale_journal.id,
            'invoice_journal_id': test_sale_journal.id,
            'payment_method_ids': [(0, 0, {
                'name': 'Cash restaurant',
                'split_transactions': True,
                'receivable_account_id': account_receivable.id,
                'journal_id': cash_journal.id,
            })],
        })

    def test_01_pos_blind_closing(self):
        self.pos_config.with_user(self.main_user).open_session_cb(check_coa=False)
        self.start_tour(
            '/pos/ui?config_id=%d' % self.pos_config.id,
            'pos_blind_close_ClosePosPopup',
            login='admin')
