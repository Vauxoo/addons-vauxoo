# coding: utf-8

from openerp.tests import common
import time


class TestTaxCommon(common.TransactionCase):

    def setUp(self):
        super(TestTaxCommon, self).setUp()
        self.account_voucher_model = self.registry('account.voucher')
        self.account_voucher_line_model = self.registry('account.voucher.line')
        self.account_invoice_model = self.registry('account.invoice')
        self.account_invoice_line_model = self.registry('account.invoice.line')
        self.acc_bank_stmt_model = self.registry('account.bank.statement')
        self.acc_bank_stmt_line_model = self.registry(
            'account.bank.statement.line')
        self.account_bnk_id = self.ref("account.bnk")
        self.partner_agrolait_id = self.ref("base.res_partner_2")
        self.account_payable_id = self.ref("account.a_pay")
        self.account_receivable_id = self.ref("account.a_recv")
        self.product_id = self.ref("product.product_product_4")
        self.invoice_journal_id = self.ref("account.sales_journal")
        self.invoice_supplier_journal_id = self.ref("account.expenses_journal")
        self.bank_journal_id = self.ref("account.bank_journal")
        self.bank_journal_usd_id = self.ref("account.bank_journal_usd")
        self.currency_usd_id = self.ref("base.USD")
        self.currency_eur_id = self.ref("base.EUR")
        self.acc_loss_tax = self.ref("account.income_fx_expense")
        self.acc_gain_tax = self.ref("account.income_fx_income")
        self.company_id = self.ref("base.main_company")
        # set expense_currency_exchange_account_id and
        # income_currency_exchange_account_id to a random account
        self.registry("res.company").write(
            self.cr, self.uid, [self.company_id],
            {'expense_currency_exchange_account_id': self.acc_loss_tax,
             'income_currency_exchange_account_id': self.acc_gain_tax})

        # Data to tax
        self.tax_16 = self.ref(
            "account_voucher_tax.account_voucher_tax_purchase_iva16")
        self.tax_0 = self.ref(
            "account_voucher_tax.account_voucher_tax_purchase_0iva")
        self.tax_16_customer = self.ref(
            "account_voucher_tax.account_voucher_tax_sale_ova16")
        self.tax_ret = self.ref(
            "account_voucher_tax."
            "account_voucher_tax_purchase_iva1067_retencion_iva")

        # Data account to tax
        self.acc_tax16 = self.ref(
            "account_voucher_tax.account_iva_voucher_16")
        self.acc_tax0 = self.ref(
            "account_voucher_tax.account_iva_voucher0_purchase_0")
        self.acc_tax16_customer = self.ref(
            "account_voucher_tax.account_ova_voucher_16")
        self.acc_ret1067 = self.ref(
            "account_voucher_tax.account_iva_voucher_retencion_iva_1067")
        self.acc_tax_pending_apply = self.ref(
            "account_voucher_tax.account_iva_voucher_pending_apply")

        self.acc_tax_16_payment = self.ref(
            "account_voucher_tax.account_iva_voucher")
        self.acc_tax_0_payment = self.ref(
            "account_voucher_tax.account_iva_voucher0_purchase")
        self.acc_tax_16_payment_customer = self.ref(
            "account_voucher_tax.account_ova_voucher")
        self.acc_ret1067_payment = self.ref(
            "account_voucher_tax.account_iva_voucher1067_retencion_iva")

        # Data to Provision tax
        self.acc_provision_tax_16_customer = self.ref(
            "account_voucher_tax.account_provision_iva_sale_16")
        self.acc_provision_tax_16_supplier = self.ref(
            "account_voucher_tax.account_provision_iva_purchase_16")
        self.provision_tax16_supplier = self.ref(
            "account_voucher_tax.account_provision_tax_purchase_ova16")
        self.provision_tax16_customer = self.ref(
            "account_voucher_tax.account_provision_tax_sale_ova16")
        self.journal_bank_special = self.ref(
            "account_voucher_tax.bank_journal_special")
        self.journal_bank_special_usd = self.ref(
            "account_voucher_tax.bank_journal_special_usd")
        # Set in company tax_provision_customer, tax_provision_supplier fields
        self.registry("res.company").write(
            self.cr, self.uid, [self.company_id],
            {'tax_provision_customer': self.provision_tax16_customer,
             'tax_provision_supplier': self.provision_tax16_supplier})

    def create_statement(self, cr, uid, line_invoice, partner, amount, journal,
                         date_bank=None, account_id=None, currency=None,
                         amount_currency=0):
        bank_stmt_id = self.acc_bank_stmt_model.create(cr, uid, {
            'journal_id': journal,
            'date': date_bank or time.strftime('%Y') + '-07-01',
        })

        bank_stmt_line_id = self.acc_bank_stmt_line_model.create(cr, uid, {
            'name': 'payment',
            'statement_id': bank_stmt_id,
            'partner_id': partner,
            'amount': amount,
            'currency_id': currency,
            'amount_currency': amount_currency,
            'date': date_bank or time.strftime('%Y') + '-07-01'})
        amount = amount_currency and amount_currency or amount

        val = {
            'credit': amount > 0 and amount or 0,
            'debit': amount < 0 and amount * -1 or 0,
            'name': line_invoice and line_invoice.name or 'cash flow'}

        if line_invoice:
            val.update({'counterpart_move_line_id': line_invoice.id})

        if account_id:
            val.update({'account_id': account_id})

        self.acc_bank_stmt_line_model.process_reconciliation(
            cr, uid, bank_stmt_line_id, [val])

        move_line_ids_complete = self.acc_bank_stmt_model.browse(
            cr, uid, bank_stmt_id).move_line_ids

        return move_line_ids_complete

    def create_invoice_supplier(
            self, cr, uid, amount_total, taxes_line, date, currency=False):
        invoice_id = self.account_invoice_model.create(
            cr, uid, {
                'partner_id': self.partner_agrolait_id,
                'journal_id': self.invoice_supplier_journal_id,
                'reference_type': 'none',
                'name': 'invoice to supplier',
                'account_id': self.account_payable_id,
                'type': 'in_invoice',
                'date_invoice': date,
                'check_total': amount_total,
            })
        if currency:
            self.account_invoice_model.write(
                cr, uid, invoice_id, {'currency_id': currency})
        self.account_invoice_line_model.create(cr, uid, {
            'product_id': self.product_id,
            'quantity': 1,
            'price_unit': 100,
            'invoice_line_tax_id': [(6, 0, taxes_line)],
            'invoice_id': invoice_id,
            'name': 'product that cost 100'})
        return invoice_id
