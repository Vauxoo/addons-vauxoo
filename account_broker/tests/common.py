from openerp.tests import common
import time


class TestTaxCommon(common.TransactionCase):

    def setUp(self):
        super(TestTaxCommon, self).setUp()
        cr, uid = self.cr, self.uid
        imd_model = self.registry("ir.model.data")
        self.inv_model = self.registry('account.invoice')
        self.voucher_model = self.registry('account.voucher')
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
        _, self.account_receivable_id = imd_model.get_object_reference(
            cr, uid, "account", "a_recv")
        _, self.account_voucher_tax_16 = imd_model.get_object_reference(
            cr, uid, "account_voucher_tax", "account_iva_voucher_16")