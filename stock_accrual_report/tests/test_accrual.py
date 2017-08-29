# -*- coding: utf-8 -*-

from openerp.tests.common import TransactionCase
from openerp.tools.safe_eval import safe_eval


class TestAccrual(TransactionCase):

    def setUp(self):
        super(TestAccrual, self).setUp()
        self.aml_obj = self.env['account.move.line']
        self.radiogram_id = self.env.ref(
            'stock_accrual_report.product_02_radiogram')
        prd_id = self.radiogram_id
        self.stock_in = prd_id.property_stock_account_input
        self.stock_out = prd_id.property_stock_account_output
        self.stock_in.reconcile = True
        self.stock_out.reconcile = True
        self.std_obj = self.env['stock.transfer_details']
        self.srp_obj = self.env['stock.return.picking']
        self.sp_obj = self.env['stock.picking']
        self.po_obj = self.env['purchase.order']
        self.so_obj = self.env['sale.order']
        self.sio_obj = self.env['stock.invoice.onshipping']
        self.expenses_journal_id = self.ref('account.expenses_journal')
        self.res = {
            '01': {'act': 'purchase', 'xml_id': "sau_po_sar_01"},
            '02': {'act': 'sale', 'xml_id': "sau_so_sar_01"}}

    def process_invoice(self, obj):
        if obj._name == 'purchase.order':
            j_id = self.expenses_journal_id
        elif obj._name == 'sale.order':
            j_id = self.expenses_journal_id
        values = {'journal_id': j_id}
        sp_brw = obj.picking_ids.filtered(
            lambda sp: sp.invoice_state == '2binvoiced')
        ctx = {'active_ids': [p.id for p in sp_brw],
               "active_model": "stock.picking"}
        sio_brw = self.sio_obj.with_context(ctx).create(values)
        ctx = {"active_ids": [p.id for p in sp_brw],
               "active_id": sp_brw.id}
        sio_brw.with_context(ctx).create_invoice()
        obj.invoice_ids.signal_workflow('invoice_open')

    def process_picking(self, sp_brws):
        sp_brws.action_confirm()
        sp_brws.action_assign()
        while sp_brws.filtered(lambda x: x.state == 'assigned'):
            sp_brw = sp_brws.filtered(lambda x: x.state == 'assigned')
            std_brw = self.std_obj.create({'picking_id': sp_brw.id})
            std_brw.do_detailed_transfer()
        return

    def get_ref(self, xml_id):
        return self.env.ref("stock_accrual_report.%s" % xml_id)

    def do_sale(self, xml_id, act_type):
        so_brw = self.get_ref(xml_id)
        if act_type == 'approval':
            so_brw.signal_workflow('order_confirm')
        elif act_type == 'transfer':
            self.process_picking(so_brw.picking_ids)
        return so_brw

    def do_purchase(self, xml_id, act_type):
        po_brw = self.get_ref(xml_id)
        if act_type == 'approval':
            po_brw.signal_workflow('purchase_confirm')
            po_brw.signal_workflow('purchase_approve')
        elif act_type == 'transfer':
            self.process_picking(po_brw.picking_ids)
        return po_brw

    def test_01_purchase_accrual_test(self):
        """ Description:
        - Approve a Purchase Order, assert state
        - Check for the `unreconciled_lines` field
        - Check for the `reconciliation_pending` field
        - Check for the `aml_ids` field
        - Make Reception of products
        - Check for the `accrual_view` method
        - Create & Approve Invoice
        - Reconcile Accruals
        - Test Cancel Invoice
        """
        record = self.res['01']
        xml_id = record['xml_id']
        po_brw = self.do_purchase(xml_id, 'approval')
        self.assertEqual(
            po_brw.state, 'approved', 'Purchase Order should be approved')
        self.assertEqual(
            po_brw.unreconciled_lines, 0, 'Unreconciled Lines should be zero')
        self.assertEqual(
            po_brw.reconciliation_pending, 0,
            'To be reconciled should be zero')
        self.assertEqual(
            len(po_brw.aml_ids), 0, 'There should be no lines at all')

        po_brw = self.do_purchase(xml_id, 'transfer')

        self.assertEqual(
            len(po_brw.aml_ids), 2, 'There should be two lines')
        ul = po_brw.search(
            [('unreconciled_lines', '=', 1),
             ('id', '=', po_brw.id)])
        self.assertEqual(
            len(ul), 1, 'One Purchase there should be in the search')
        self.assertEqual(
            po_brw.unreconciled_lines, 1, 'Unreconciled Lines should be one')
        self.assertEqual(
            po_brw.reconciliation_pending, 0,
            'To be reconciled should be zero')

        # This should not affect the results
        po_brw.reconcile_stock_accrual()

        self.assertEqual(
            len(po_brw.aml_ids), 2, 'There should be two lines')
        ul = po_brw.search(
            [('unreconciled_lines', '=', 1),
             ('id', '=', po_brw.id)])
        self.assertEqual(
            len(ul), 1, 'One Purchase there should be in the search')
        self.assertEqual(
            po_brw.unreconciled_lines, 1, 'Unreconciled Lines should be one')
        self.assertEqual(
            po_brw.reconciliation_pending, 0,
            'To be reconciled should be zero')

        self.process_invoice(po_brw)

        self.assertEqual(
            len(po_brw.aml_ids), 3, 'There should be three lines')
        self.assertEqual(
            po_brw.unreconciled_lines, 2, 'Unreconciled Lines should be Two')
        pl = po_brw.search(
            [('reconciliation_pending', '=', 2),
             ('id', '=', po_brw.id)])
        self.assertEqual(
            len(pl), 1, 'One Purchase there should be in the search')
        self.assertEqual(
            po_brw.reconciliation_pending, 2, 'To be reconciled should be Two')

        po_brw.cron_purchase_accrual_reconciliation()
        self.assertEqual(
            po_brw.unreconciled_lines, 0, 'Unreconciled Lines should be zero')
        self.assertEqual(
            po_brw.reconciliation_pending, 0,
            'To be reconciled should be zero')

        view_accrual = po_brw.view_accrual()
        self.assertTrue(
            'domain' in view_accrual,
            'There is something wrong with `view_accrual`')
        domain = safe_eval(view_accrual['domain'])
        self.assertTrue(
            isinstance(domain, list),
            'There is something wrong with `view_accrual` domain')
        self.assertTrue(
            isinstance(domain[0], tuple) and len(domain[0]) == 3,
            'There is something wrong with `view_accrual` domain args')
        self.assertTrue(
            isinstance(domain[0][2], list),
            'Something wrong with `view_accrual` domain args operands')
        self.assertTrue(
            set(domain[0][2]).issubset(set(po_brw.aml_ids._ids)),
            'Something wrong with `view_accrual` returned data')

        return

    def test_02_sale_accrual_test(self):
        """ Description:
        - Approve a Sale Order, assert state
        - Check for the `unreconciled_lines` field
        - Check for the `reconciliation_pending` field
        - Check for the `aml_ids` field
        - Make Reception of products
        - Check for the `accrual_view` method
        - Create & Approve Invoice
        - Reconcile Accruals
        - Test Cancel Invoice
        """
        xml_id = self.res['01']['xml_id']
        self.do_purchase(xml_id, 'approval')
        self.do_purchase(xml_id, 'transfer')

        record = self.res['02']
        xml_id = record['xml_id']
        so_brw = self.do_sale(xml_id, 'approval')
        self.assertEqual(
            so_brw.state, 'progress', 'Sale Order should be approved')
        self.assertEqual(
            so_brw.unreconciled_lines, 0, 'Unreconciled Lines should be zero')
        self.assertEqual(
            so_brw.reconciliation_pending, 0,
            'To be reconciled should be zero')
        self.assertEqual(
            len(so_brw.aml_ids), 0, 'There should be no lines at all')

        so_brw = self.do_sale(xml_id, 'transfer')

        self.assertEqual(
            len(so_brw.aml_ids), 4, 'There should be four lines')
        ul = so_brw.search(
            [('unreconciled_lines', '=', 2),
             ('id', '=', so_brw.id)])
        self.assertEqual(
            len(ul), 1, 'One Sale there should be in the search')
        self.assertEqual(
            so_brw.unreconciled_lines, 2, 'Unreconciled Lines should be two')
        self.assertEqual(
            so_brw.reconciliation_pending, 0,
            'To be reconciled should be zero')

        self.env['res.company'].browse(self.uid).do_partial = True
        so_brw.reconcile_stock_accrual()
        pl = so_brw.aml_ids.mapped('reconcile_partial_id')
        self.assertEqual(
            len(pl), 1, 'There should one partial reconciliation')

        self.process_invoice(so_brw)

        self.assertEqual(
            len(so_brw.aml_ids), 6, 'There should be six lines')
        self.assertEqual(
            so_brw.unreconciled_lines, 4, 'Unreconciled Lines should be Four')
        pl = so_brw.search(
            [('reconciliation_pending', '=', 4),
             ('id', '=', so_brw.id)])
        self.assertEqual(
            len(pl), 1, 'One Purchase there should be in the search')
        self.assertEqual(
            so_brw.reconciliation_pending, 4, 'Four to reconciled')

        so_brw.cron_sale_accrual_reconciliation()
        self.assertEqual(
            so_brw.unreconciled_lines, 0, 'Unreconciled Lines should be zero')
        self.assertEqual(
            so_brw.reconciliation_pending, 0,
            'To be reconciled should be zero')

        view_accrual = so_brw.view_accrual()
        self.assertTrue(
            'domain' in view_accrual,
            'There is something wrong with `view_accrual`')
        domain = safe_eval(view_accrual['domain'])
        self.assertTrue(
            isinstance(domain, list),
            'There is something wrong with `view_accrual` domain')
        self.assertTrue(
            isinstance(domain[0], tuple) and len(domain[0]) == 3,
            'There is something wrong with `view_accrual` domain args')
        self.assertTrue(
            isinstance(domain[0][2], list),
            'Something wrong with `view_accrual` domain args operands')
        self.assertTrue(
            set(domain[0][2]).issubset(set(so_brw.aml_ids._ids)),
            'Something wrong with `view_accrual` returned data')

        return
