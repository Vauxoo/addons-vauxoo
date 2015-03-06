from openerp.addons.account_broker.tests.common import TestTaxCommon
import time


class TestInvoiceVoucherBroker(TestTaxCommon):
    """
    This test is to check that when I create a invoice to 'Reposicion de
    gastos' this invoice not create 'Iva efectivamente pagado' to this invoice,
    only to invoice that send me the broker from mi supplier.
    """

    def setUp(self):
        super(TestInvoiceVoucherBroker, self).setUp()

    def test_programmatic_tax(self):
        """
        This method test the feature wuth account.voucher
        """
        cr, uid = self.cr, self.uid
        # I create the invoice to broker
        context = {'default_type': 'in_invoice'}
        inv_id = self.inv_model.create(cr, uid, dict(
            account_id=self.account_inv,
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
        voucher_id = self.voucher_model.create(cr, uid, dict(
            name='Payment invoice broker',
            account_id=self.account_vou,
            company_id=self.company_id,
            amount=7694.20,
            journal_id=self.journal_vou_id,
            partner_id=self.partner_id,
            date=time.strftime("%Y-%m-%d"),
            type='payment',
        ))

        # I call onchange to amount to load lines to voucher
        res_onch = self.voucher_model.onchange_amount(
            cr, uid, [voucher_id], 7694.20, 1.0, self.partner_id,
            self.journal_vou_id, self.currency_id,
            'payment', time.strftime("%Y-%m-%d"),
            self.currency_id, self.company_id)
        line_dr = res_onch.get('value', {}).get('line_dr_ids', [{}])[0]
        line_dr.update({'voucher_id': voucher_id})
        self.voucher_model_line.create(cr, uid, line_dr)

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

        cr.commit()
