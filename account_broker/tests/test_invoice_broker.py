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

    def test_programmatic_tax(self):
        cr, uid = self.cr, self.uid
        # I create the invoice to broker
        context = {'default_type': 'in_invoice'}
        inv_id = self.inv_model.create(cr, uid, dict(
            account_id=self.account_receivable_id,
            partner_id=self.partner_id,
            check_total=7694.20,
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

        # I check the total to invoice created
        self.assertEquals(self.inv_model.read(
            cr, uid, inv_id,
            ['amount_total']).get('amount_total', 0.0), 7694.20)

        # I check the state of invoice is open
        self.assertEquals(self.inv_model.read(
            cr, uid, inv_id, ['state']).get('state', ''), 'open')

        # I try pay the invoice, I create the payment
        move_line_id = False
        move_tax = False
        for move in self.inv_model.browse(cr, uid, inv_id).move_id.line_id:
            if move.account_id.id == self.account_receivable_id:
                move_line_id = move.id
            elif move.debit == 1039.20:
                move_tax = move.id
        voucher_id = self.voucher_model.create(cr, uid, dict(
            name='Payment invoice broker',
            account_id=self.account_vou,
            company_id=self.company_id,
            amount=7694.20,
            journal_id=self.journal_vou_id,
            partner_id=self.partner_id,
            date=time.strftime("%Y-%m-%d"),
            type='payment',
            line_dr_ids=[(0, 0, {
                'amount': 7694.20,
                'type': 'dr',
                'partner_id': self.partner_id,
                'account_id': self.account_receivable_id,
                'move_line_id': move_line_id,
                'tax_line_ids': [(0, 0, {
                    'tax_id': self.tax_16_id,
                    'account_id': self.account_voucher_tax_16,
                    'amount_tax': 1039.20,
                    'move_line_id': move_tax,
                    'original_tax': 1039.20
                })]
            })]
        ))

        # I try validate the payment
        self.voucher_model.signal_workflow(
            cr, uid, [voucher_id], 'proforma_voucher')

        # I check that the payment state is posted
        self.assertEquals(self.voucher_model.read(
            cr, uid, voucher_id,
            ['state']).get('state', ''), 'posted')

        # I check the status to invoice == 'paid'
        self.assertEquals(self.inv_model.read(
            cr, uid, inv_id, ['state']).get('state', ''), 'paid')

        # I check the journal entry to the invoice
        move_inv = self.inv_model.browse(cr, uid, inv_id).move_id
        error = False
        for line in move_inv.line_id:
            if line.partner_id.id != self.partner_id:
                if not line.amount_base and not line.tax_id_secondary:
                    error = True
        if error:
            self.assertEquals(0, 1, "The invoice have not line to report in "
                              "DIOT to supplier broker")

        # I check the hournal entro from payment
        move_pay = self.voucher_model.browse(cr, uid, voucher_id).move_id
        total_lines = 0
        for line in move_pay.line_id:
            if line.partner_id.id == self.partner_id:
                total_lines += 1
            else:
                self.assertEquals(1, 0, "Only must be lines wth the same "
                                  "supplier that the invoice")
        self.assertEquals(
            4, total_lines, "The move payment must be have 4 lines to the same"
            " supplier of invoice")
