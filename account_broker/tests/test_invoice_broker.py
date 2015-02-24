from openerp.tests.common import TransactionCase
import time

class TestTInvoiceBroker(TransactionCase):
    """
    TODO
    """

    def setUp(self):
        super(TestTInvoiceBroker, self).setUp()
        cr, uid = self.cr, self.uid
        imd_model = self.registry("ir.model.data")
        self.inv_model = self.registry('account.invoice')
        self.voucher_model = self.registry('account.voucher')
        _, self.account_inv = imd_model.get_object_reference(
            cr, uid, "account", "a_pay")
        _, self.account_vou = imd_model.get_object_reference(
            cr, uid, "account", "cash")
        _, self.partner_id = imd_model.get_object_reference(
            cr, uid, "account_broker", "res_partner_supplier_broker")
        _, self.company_id = imd_model.get_object_reference(
            cr, uid, "base", "main_company")
        _, self.currency_id = imd_model.get_object_reference(
            cr, uid, "base", "MXN")
        _, self.journal_inv_id = imd_model.get_object_reference(
            cr, uid, "account", "expenses_journal")
        _, self.journal_vou_id = imd_model.get_object_reference(
            cr, uid, "account", "bank_journal")
        _, self.acc_line_id = imd_model.get_object_reference(
            cr, uid, "account", "a_expense")
        _, self.prod_line1 = imd_model.get_object_reference(
            cr, uid, "account_broker", "product_product_broker_payment")
        _, self.prod_line2 = imd_model.get_object_reference(
            cr, uid, "product", "product_product_39")
        _, self.tax_brok16_id = imd_model.get_object_reference(
            cr, uid, "account_broker", "account_tax_purchase_iva16_broker")
        _, self.tax_16_id = imd_model.get_object_reference(
            cr, uid, "account_voucher_tax",
            "account_voucher_tax_purchase_iva16")
        _, self.tax_inv_2_id = imd_model.get_object_reference(
            cr, uid, "account", "test_invoice_1")

    def test_programmatic_tax(self):
        cr, uid = self.cr, self.uid
        # I create the invoice to broker
        context = {'default_type': 'in_invoice'}
        inv_id = self.inv_model.create(cr, uid, dict(
            account_id=self.account_inv,
            partner_id=self.partner_id,
            check_total=160.0,
            company_id=self.company_id,
            currency_id=self.currency_id,
            journal_id=self.journal_inv_id,
            reference_type='none',
            invoice_line=[(0, 0, {
                'name': '[Importation]Product for importation',
                'account_id': self.acc_line_id,
                'price_unit': 1000.0,
                'product_id': self.prod_line1,
                'quantity': 0,
                'invoice_line_tax_id': [(6, 0, [self.tax_brok16_id])],
                'invoice_broker_id': self.tax_inv_2_id
            }), (0, 0, {
                'name': '[Importation]Product for importation',
                'account_id': self.acc_line_id,
                'price_unit': 1299.0,
                'product_id': self.prod_line2,
                'quantity': 5,
                'invoice_line_tax_id': [(6, 0, [self.tax_16_id])]
            })]
        ), context=context)

        # I try validate the invoice
        self.inv_model.signal_workflow(cr, uid, [inv_id], 'invoice_open')

        self.assertEquals(self.inv_model.read(
            cr, uid, inv_id,
            ['amount_total']).get('amount_total', 0.0), 7694.20)

        self.assertEquals(self.inv_model.read(
            cr, uid, inv_id, ['state']).get('state', ''), 'open')

        self.inv_model.signal_workflow(cr, uid, [inv_id], 'reconciled')

        # I try pay the invoice, I create the payment
        # voucher_id = self.voucher_model.create(cr, uid, dict(
        #     name='Payment invoice broker',
        #     account_id=self.account_vou,
        #     company_id=self.company_id,
        #     amount=7694.20,
        #     journal_id=self.journal_vou_id,
        #     partner_id=self.partner_id,
        #     date=time.strftime("%Y-%m-%d"),
        #     type='payment'
        # ))

        # I try validate the payment
        # self.voucher_model.signal_workflow(
        #     cr, uid, [voucher_id], 'proforma_voucher')

        # self.assertEquals(self.voucher_model.read(
        #     cr, uid, voucher_id,
        #     ['state']).get('state', ''), 'posted')

        # I check the status to invoice == 'paid'
        #     cr, uid, inv_id, ['state']).get('state', '')
        # self.assertEquals(self.inv_model.read(
        #     cr, uid, inv_id, ['state']).get('state', ''), 'paid')

