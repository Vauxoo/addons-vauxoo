# coding: utf-8
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: hugo@vauxoo.com
#    planned by: Nhomar Hernandez <nhomar@vauxoo.com>
############################################################################
from openerp.tests.common import TransactionCase
from datetime import date
from openerp import exceptions
from datetime import datetime, timedelta


class TestStockPickingInvoiceValidation(TransactionCase):
    """
        This Tests validate the payment type dependig
        payment terms line to compute
    """
    def setUp(self):
        super(TestStockPickingInvoiceValidation, self).setUp()
        self.sale_order = self.env['sale.order']
        # China export
        self.china_export = self.env.ref('base.res_partner_3')
        self.company = self.env.user.company_id
        self.warehouse = self.env.ref('stock.warehouse0')
        self.ref_char = "stock_picking_invoice_validation." + \
                        "stock_production_lot_10"
        self.pay_account_id = self.env['account.account'].\
            browse(self.ref("account.cash"))
        self.journal_id = self.env['account.journal'].\
            browse(self.ref("account.bank_journal"))
        date_start = date.today().replace(day=1, month=1).strftime('%Y-%m-%d')
        self.period_id = self.env['account.fiscalyear'].search(
            [('date_start', '=', date_start)]).period_ids[8]
        self.account_id = self.env.ref("account.a_recv")

    def create_lot_and_wizards_transfer(self, sale_order):
        # Transferir los productos del picking de la orden
        # de compra
        wizards = []
        transfer_obj = self.env['stock.transfer_details']
        transfer_item_obj = self.env['stock.transfer_details_items']
        lot_ids = [
            self.env.ref(self.ref_char + str(num)) for num in xrange(4, 7)]
        for idx, picking in enumerate(sale_order.picking_ids):
            wizard_transfer_id = transfer_obj.create({
                'picking_id': picking.id,
            })
            for stock_move in picking.move_lines:
                lot_id = lot_ids[idx]

                transfer_item_obj.create({
                    'transfer_id': wizard_transfer_id.id,
                    'product_id': stock_move.product_id.id,
                    'quantity': stock_move.product_qty,
                    'sourceloc_id': stock_move.location_id.id,
                    'destinationloc_id': stock_move.location_dest_id.id,
                    'lot_id': lot_id.id,
                    'product_uom_id': stock_move.product_uom.id,
                })
            wizards.append(wizard_transfer_id)
        return wizards

    def create_sale_order_lines(self, sale):
        sale_line_obj = self.env['sale.order.line']
        product4 = self.env.ref('product.product_product_4')
        sale_line_obj.create({
            'name': product4.name,
            'delay': 0,
            'order_id': sale.id,
            'company_id': self.company.id,
            'price_unit': product4.standard_price,
            'product_uom': product4.uom_id.id,
            'product_id': product4.id,
            'product_uom_qty': 1,
        })

    def create_sale_order(self):
        sale = self.sale_order.create({
            'name': 'Sale Order Test',
            'company_id': self.env.user.company_id.id,
            'partner_id': self.china_export.id,
            'order_policy': 'manual',
            'check_invoice': 'check',
            'picking_policy': 'direct',
            'warehouse_id': self.warehouse.id,
        })
        return sale

    def sale_validate_invoice(self, sale):
        sale_advance_obj = self.env['sale.advance.payment.inv']
        context = {
            'active_model': 'sale.order',
            'active_ids': [sale.id],
            'active_id': sale.id,
        }
        wizard_invoice_id = sale_advance_obj.with_context(context).create({
            'advance_payment_method': 'all',
        })
        wizard_invoice_id.with_context(context).create_invoices()
        for invoice_id in sale.invoice_ids:
            invoice_id.signal_workflow('invoice_open')
            # check if invoice is open
            self.assertEqual(invoice_id.state, 'open')
            invoice_id.pay_and_reconcile(
                invoice_id.amount_total, self.pay_account_id.id,
                self.period_id.id, self.journal_id.id, self.pay_account_id.id,
                self.period_id.id, self.journal_id.id,
                name="Payment for Invoice")
            # in order to proceed is necessary to get the sale order invoiced
            # and the invoice paid as well
            self.assertTrue(sale.invoiced)
            self.assertEqual(invoice_id.state, 'paid')

    def test_00_validate_the_correct_invoice(self):
        """
            This test validates that is registered the correct invoice
            in the picking
        """
        invoice_2 = self.env.ref('sale.test_crm_sale_invoice_2')

        sale = self.create_sale_order()
        self.create_sale_order_lines(sale)
        sale.action_button_confirm()
        self.sale_validate_invoice(sale)
        wizards = self.create_lot_and_wizards_transfer(sale)
        for wiz in wizards:
            if not wiz.picking_id.picking_type_code == 'outgoing':
                # TODO data demo need to be update to give availability to the
                # product used in the picking. This way we could use
                # action_assign instead force_assign
                # wiz.picking_id.action_assign()
                wiz.picking_id.force_assign()
                wiz.do_detailed_transfer()
            else:
                wiz.invoice_id = invoice_2
                # Try to transfer picking with a wrong invoice
                with self.assertRaises(exceptions.Warning):
                    # TODO data demo need to be update to give availability to
                    # the product used in the picking. This way we could use
                    # action_assign instead force_assign
                    # wiz.picking_id.action_assign()
                    wiz.picking_id.force_assign()
                    wiz.do_detailed_transfer()
                # Try to transfer picking with a the correct invoice
                wiz.invoice_id = sale.invoice_ids
                # TODO data demo need to be update to give availability to the
                # product used in the picking. This way we could use
                # action_assign instead force_assign
                # wiz.picking_id.action_assign()
                wiz.picking_id.force_assign()
                wiz.do_detailed_transfer()

    def test_01_validate_products_and_qtys(self):
        """
            This test validates that an invoice has the correct products and
            qty vs the moves picking
        """
        product = self.env.ref('product.product_product_4')
        invoice_id2 = self.env['account.invoice'].create(
            {'partner_id': self.china_export.id,
             'account_id': self.account_id.id,
             'date_invoice': (
                 datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
             'journal_id': self.journal_id.id, })
        self.env['account.invoice.line'].create(
            {'product_id': product.id,
             'quantity': 4,
             'price_unit': 100,
             'invoice_id': invoice_id2.id,
             'name': 'product that cost 100', })
        # Validate the invoice.
        invoice_id2.signal_workflow('invoice_open')
        invoice_id2.pay_and_reconcile(
            invoice_id2.amount_total, self.pay_account_id.id,
            self.period_id.id, self.journal_id.id, self.pay_account_id.id,
            self.period_id.id, self.journal_id.id,
            name="Payment for Invoice")

        sale = self.create_sale_order()
        self.create_sale_order_lines(sale)
        sale.action_button_confirm()
        self.sale_validate_invoice(sale)
        wizards = self.create_lot_and_wizards_transfer(sale)
        for wiz in wizards:
            if not wiz.picking_id.picking_type_code == 'outgoing':
                # TODO data demo need to be update to give availability to the
                # product used in the picking. This way we could use
                # action_assign instead force_assign
                # wiz.picking_id.action_assign()
                wiz.picking_id.force_assign()
                wiz.do_detailed_transfer()
            else:
                wiz.invoice_id = invoice_id2
                # Try to transfer picking with a wrong invoice
                with self.assertRaises(exceptions.Warning):
                    # TODO data demo need to be update to give availability to
                    # the product used in the picking. This way we could use
                    # action_assign instead force_assign
                    # wiz.picking_id.action_assign()
                    wiz.picking_id.force_assign()
                    wiz.do_detailed_transfer()
                # Try to transfer picking with a the correct invoice
                wiz.invoice_id = sale.invoice_ids

                # TODO data demo need to be update to give availability to the
                # product used in the picking. This way we could use
                # action_assign instead force_assign
                # wiz.picking_id.action_assign()
                wiz.picking_id.force_assign()
                wiz.do_detailed_transfer()

    def test_02_validate_the_registered_invoice(self):
        """
            This test validates that is registered the correct invoice
            in no more than one picking
        """

        sale = self.create_sale_order()
        self.create_sale_order_lines(sale)
        sale.action_button_confirm()
        self.sale_validate_invoice(sale)
        wizards1 = self.create_lot_and_wizards_transfer(sale)

        sale2 = self.sale_order.create({
            'name': 'Sale Order Test2',
            'company_id': self.env.user.company_id.id,
            'partner_id': self.china_export.id,
            'order_policy': 'manual',
            'check_invoice': 'check',
            'picking_policy': 'direct',
            'warehouse_id': self.warehouse.id,
        })
        self.create_sale_order_lines(sale2)
        sale2.action_button_confirm()
        self.sale_validate_invoice(sale2)
        wizards2 = self.create_lot_and_wizards_transfer(sale2)
        for wiz in wizards2:
            if not wiz.picking_id.picking_type_code == 'outgoing':
                # TODO data demo need to be update to give availability to the
                # product used in the picking. This way we could use
                # action_assign instead force_assign
                # wiz.picking_id.action_assign()
                wiz.do_detailed_transfer()
            else:
                # Registerd in wizads2 the sale.invoice_ids
                wiz.invoice_id = sale.invoice_ids
                # TODO data demo need to be update to give availability to the
                # product used in the picking. This way we could use
                # action_assign instead force_assign
                # wiz.picking_id.action_assign()
                wiz.picking_id.force_assign()
                wiz.do_detailed_transfer()

        for wiz in wizards1:
            if not wiz.picking_id.picking_type_code == 'outgoing':
                # TODO data demo need to be update to give availability to the
                # product used in the picking. This way we could use
                # action_assign instead force_assign
                # wiz.picking_id.action_assign()
                wiz.picking_id.force_assign()
                wiz.do_detailed_transfer()
            else:
                # Registerd for second time the sale.invoice_ids
                wiz.invoice_id = sale.invoice_ids
                with self.assertRaises(exceptions.Warning):
                    # TODO data demo need to be update to give availability to
                    # the product used in the picking. This way we could use
                    # action_assign instead force_assign
                    # wiz.picking_id.action_assign()
                    wiz.picking_id.force_assign()
                    wiz.do_detailed_transfer()
