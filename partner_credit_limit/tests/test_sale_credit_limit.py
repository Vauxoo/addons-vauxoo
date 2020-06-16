# coding: utf-8
# Copyright 2016 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime, timedelta
from odoo.exceptions import ValidationError
from . import common


class TestSalesCreditLimits(common.TestCommon):
    """This test Validate credit limit, late pyaments and credit
        overloaded.
    """
    def setUp(self):
        super(TestSalesCreditLimits, self).setUp()
        self._load('account', 'test', 'account_minimal_test.xml')
        self.sale_order = self.env['sale.order']
        self.sale_order_line = self.env['sale.order.line']
        self.payment_term_credit = self.env.ref(
            'account.account_payment_term_advance')
        self.pricelist = self.env.ref('product.list0')

        self.partner_china = self.env.ref("base.res_partner_3")
        self.journal_id = self.env.ref("account.bank_journal")
        self.account_id = self.env.ref("account.a_recv")
        self.account_sale_id = self.env.ref("account.a_sale")
        self.product_id = self.env.ref("product.product_product_6")
        self.mxn_currency = self.env.ref('base.MXN')
        self.usd_currency = self.env.ref('base.USD')

    def test_credit_limit_overloaded(self):
        """This test validate the partner has credit overloaded
            and can not confirm the sale order

        """
        # CASE WHERE PARTNER HAVE CREDIT OVERLOADED
        # set credit limit in 500
        self.partner_china.credit_limit = 200.00

        # sale order with amount total of 600.00
        sale_id = self.sale_order.create(
            {'partner_id': self.partner_china.id,
             'payment_term_id': self.payment_term_credit.id})
        self.sale_order_line.create(
            {'product_id': self.product_id.id,
             'product_uom_qty': 1,
             'price_unit': 600,
             'order_id': sale_id.id,
             'product_uom': self.product_id.uom_id.id,
             'name': 'product that cost 100', })
        # should not confirm sale order
        # credit limit exceded
        # credit_limit = 500
        # amount_total = 600
        with self.assertRaises(ValidationError):
            sale_id.action_confirm()

        # CASE WHERE PARTNER HAVE CREDIT
        # set credit limit in 500
        self.partner_china.credit_limit = 700.00
        self.assertTrue(self.partner_china.allowed_sale,
                        "Allowed Sale should be True")
        sale_id.action_confirm()
        self.assertEqual(sale_id.state, 'sale',
                         'State of the sales order must be in sale')

    def test_partner_with_late_payments(self):
        """This test validate that the partner has not late payments

        """
        # CASE WHERE PARTNER DOES NOT HAVE LATE PAYMENTS AND CREDIT OVERLOADED
        # set credit limit in 500
        self.partner_china.credit_limit = 700.00

        # invoice with amount total of 400.00 and date decreased one day
        # to get a late payment
        invoice_id = self.account_invoice.create(
            {'partner_id': self.partner_china.id,
             'account_id': self.account_id.id,
             'date_invoice': (datetime.now() - timedelta(days=2)).
                strftime("%Y-%m-%d"),
             'payment_term_id': self.payment_term_credit.id,
             'journal_id': self.journal_id.id, })
        self.account_invoice_line.create(
            {'product_id': self.product_id.id,
             'account_id': self.account_sale_id.id,
             'quantity': 4,
             'price_unit': 100,
             'invoice_id': invoice_id.id,
             'name': 'product that cost 100', })
        # Validate the invoice.
        invoice_id.action_invoice_open()

        # At this moment there are late paymets since the invoice
        # was validate one day before

        # CASE WHERE PARTNER HAVE LATE PAYMENTS
        # sale order with amount total of 600.00
        sale_id = self.sale_order.create(
            {'partner_id': self.partner_china.id,
             'payment_term_id': self.payment_term_credit.id})
        self.sale_order_line.create(
            {'product_id': self.product_id.id,
             'product_uom_qty': 1,
             'price_unit': 200,
             'order_id': sale_id.id,
             'product_uom': self.product_id.uom_id.id,
             'name': 'product that cost 100', })
        # should not confirm sale order should fail,
        # couse there are late payments
        # since the invoice 1 was validate with curent day minus 2 days
        with self.assertRaises(ValidationError):
            sale_id.action_confirm()

    def test_credit_limit_overloaded_with_diferent_currency(self):
        """This test validate when sale exceeds the credit limit because it is
        in a different currency of sale company currency, therefore, conversion
        must be done
        """
        # Set credit limit in 600
        self.partner_china.credit_limit = 600.00

        # Sale order with amount total of 600.00, the same of partner credit
        # limit, but when conversion is done, this amount must exceed partner
        # credit limit
        self.pricelist.currency_id = self.usd_currency.id
        sale_id = self.sale_order.create(
            {'partner_id': self.partner_china.id,
                'pricelist_id': self.pricelist.id,
                'payment_term_id': self.payment_term_credit.id})
        self.sale_order_line.create(
            {'product_id': self.product_id.id,
                'product_uom_qty': 1,
                'price_unit': 600,
                'order_id': sale_id.id,
                'name': 'product that cost 100', })

        sale_id.company_id.write({'currency_id': self.mxn_currency.id})
        self.mxn_currency.rate_ids.write({'rate': 18.0})
        # Sale currency must be USD and company currency must be MXN
        self.assertNotEqual(sale_id.currency_id,
                            sale_id.company_id.currency_id)
        # Should not confirm sale order
        # Credit limit exceded when conversion is done from USD to MXN
        with self.assertRaises(ValidationError):
            sale_id.action_confirm()
