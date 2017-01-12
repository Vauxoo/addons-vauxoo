# -*- coding: utf-8 -*-

from copy import deepcopy
from datetime import datetime
from openerp.tests.common import TransactionCase


class TestStockCard(TransactionCase):

    def setUp(self):
        super(TestStockCard, self).setUp()
        self.aml_obj = self.env['account.move.line']
        self.radiogram_id = self.env.ref(
            'stock_account_unfuck.product_02_radiogram')
        self.val_id = self.radiogram_id.\
            categ_id.property_stock_valuation_account_id
        self.std_obj = self.env['stock.transfer_details']
        self.srp_obj = self.env['stock.return.picking']
        self.sp_obj = self.env['stock.picking']
        self.so_obj = self.env['sale.order']
        self.po_obj = self.env['purchase.order']
        self.res = {
            '01': {
                'act': 'purchase', 'xml': True, 'xml_id': "sau_po_ut_01",
                'avg': 100, 'qty': 10, 'debit': 1000, 'credit': 0, },
            '02': {
                'act': 'sale', 'xml': True, 'xml_id': "sau_so_ut_01",
                'avg': 100, 'qty': 6, 'debit': 1000, 'credit': 400, },
            '03': {
                'act': 'sale', 'xml': True, 'xml_id': "sau_so_ut_02",
                'avg': 100, 'qty': 1, 'debit': 1000, 'credit': 900, },
            '04': {
                'act': 'purchase', 'xml': True, 'xml_id': "sau_po_ut_02",
                'avg': 250, 'qty': 4, 'debit': 1900, 'credit': 900, },
            '05': {
                'act': 'sale', 'xml': True, 'xml_id': "sau_so_ut_03",
                'avg': 250, 'qty': 1, 'debit': 1900, 'credit': 1650, },
            '06': {
                'act': 'sale-ret', 'qty-ret': 1, 'xml_id': "sau_so_ut_01",
                'avg': 175, 'qty': 2, 'debit': 2000, 'credit': 1650, },
            '07': {
                'act': 'purchase', 'xml': True, 'xml_id': "sau_po_ut_03",
                'avg': 207.14, 'qty': 7, 'debit': 3100, 'credit': 1650, },
            '08': {
                'act': 'purchase', 'xml': True, 'xml_id': "sau_po_ut_04",
                'avg': 265, 'qty': 10, 'debit': 4300, 'credit': 1650, },
            '09': {
                'act': 'purchase-ret', 'qty-ret': 5, 'xml_id': "sau_po_ut_03",
                'avg': 310, 'qty': 5, 'debit': 4300, 'credit': 2750, },
            '10': {
                'act': 'purchase-ret', 'qty-ret': 1, 'xml_id': "sau_po_ut_02",
                'avg': 312.5, 'qty': 4, 'debit': 4300, 'credit': 3050, },
            '11': {
                'act': 'purchase-ret', 'qty-ret': 1, 'xml_id': "sau_po_ut_01",
                'avg': 383.33, 'qty': 3, 'debit': 4300, 'credit': 3150, },
            '12': {
                'act': 'purchase-ret', 'qty-ret': 3, 'xml_id': "sau_po_ut_04",
                'avg': 383.33, 'qty': 0, 'debit': 4300, 'credit': 4299.99, },
            '13': {
                'act': 'purchase', 'xml': True, 'xml_id': "sau_po_ut_05",
                'avg': 280, 'qty': 6, 'debit': 5980, 'credit': 4299.99, },
            '14': {
                'act': 'sale-ret', 'qty-ret': 3, 'xml_id': "sau_so_ut_03",
                'avg': 270, 'qty': 9, 'debit': 6730, 'credit': 4299.99, },
            '15': {
                'act': 'sale', 'xml': True, 'xml_id': "sau_so_ut_04",
                'avg': 270, 'qty': 6, 'debit': 6730, 'credit': 5109.99, },
        }

        self.res_border = {
            '13': {
                'act': 'purchase', 'border': True, 'xml_id': "sau_po_ut_05",
                'avg': 280, 'qty': 6, 'debit': 5980, 'credit': 4299.99, },
            '14': {
                'act': 'sale-ret', 'qty-ret': 3, 'xml_id': "sau_so_ut_03",
                'avg': 280, 'qty': 9, 'debit': 6820, 'credit': 4299.99, },
            '15': {
                'act': 'sale', 'xml': True, 'xml_id': "sau_so_ut_04",
                'avg': 280, 'qty': 6, 'debit': 6820, 'credit': 5139.99, },
        }

    def process_picking(self, sp_brws):
        sp_brws.action_confirm()
        sp_brws.action_assign()
        while sp_brws.filtered(lambda x: x.state == 'assigned'):
            sp_brw = sp_brws.filtered(lambda x: x.state == 'assigned')
            std_brw = self.std_obj.create({'picking_id': sp_brw.id})
            std_brw.do_detailed_transfer()
        return

    def do_sale_return(self, record):
        xml_id = record['xml_id']
        so_id = self.ref("stock_account_unfuck.%s" % xml_id)
        so_brw = self.so_obj.browse(so_id)
        active_id = so_brw.picking_ids.filtered(
            lambda x: x.picking_type_code == 'outgoing').id
        src_pck = so_brw.picking_ids.filtered(
            lambda x: x.location_id.name == 'Stock')
        src_loc_id = src_pck.location_id.id
        ctx = {'active_id': active_id, 'active_ids': [active_id]}
        field_names = ['product_return_moves', 'move_dest_exists']
        res = self.srp_obj.with_context(ctx).default_get(field_names)
        srp_brw = self.srp_obj.create({'invoice_state': 'none'})
        values = {
            'move_dest_exists': res['move_dest_exists'],
            'product_return_moves': [
                (0, 0, dict(
                    line,
                    wizard_id=srp_brw.id,
                    quantity=record['qty-ret']))
                for line in res['product_return_moves']]
        }
        srp_brw.write(values)
        sp_id = srp_brw.with_context(ctx)._create_returns()[0]
        sp_brw = self.sp_obj.browse(sp_id)
        sp_brw.move_lines.write({'location_dest_id': src_loc_id})

        self.process_picking(sp_brw)
        return

    def do_sale(self, xml_id):
        so_id = self.ref("stock_account_unfuck.%s" % xml_id)
        so_brw = self.so_obj.browse(so_id)
        so_brw.signal_workflow('order_confirm')
        so_brw.signal_workflow('manual_invoice')
        self.process_picking(so_brw.picking_ids)
        return

    def do_purchase_return(self, record):
        xml_id = record['xml_id']
        po_id = self.ref("stock_account_unfuck.%s" % xml_id)
        po_brw = self.po_obj.browse(po_id)
        active_id = po_brw.picking_ids[0].id
        ctx = {'active_id': active_id, 'active_ids': [active_id]}
        field_names = ['product_return_moves', 'move_dest_exists']
        res = self.srp_obj.with_context(ctx).default_get(field_names)
        srp_brw = self.srp_obj.create({'invoice_state': 'none'})
        values = {
            'move_dest_exists': res['move_dest_exists'],
            'product_return_moves': [
                (0, 0, dict(
                    line,
                    wizard_id=srp_brw.id,
                    quantity=record['qty-ret']))
                for line in res['product_return_moves']]
        }
        srp_brw.write(values)
        sp_id = srp_brw.with_context(ctx)._create_returns()[0]
        sp_brw = self.sp_obj.browse(sp_id)

        self.process_picking(sp_brw)
        return

    def do_purchase(self, xml_id):
        po_id = self.ref("stock_account_unfuck.%s" % xml_id)
        po_brw = self.po_obj.browse(po_id)
        po_brw.signal_workflow('purchase_confirm')
        po_brw.signal_workflow('purchase_approve')
        self.process_picking(po_brw.picking_ids)
        return

    def return_transaction(self, record):
        if record['act'] in ('sale', ):
            self.do_sale(record['xml_id'])
        elif record['act'] in ('sale-ret', ):
            self.do_sale_return(record)
        elif record['act'] in ('purchase', ):
            self.do_purchase(record['xml_id'])
        elif record['act'] in ('purchase-ret', ):
            self.do_purchase_return(record)
        return

    def test_00_average_computation(self):
        for index in range(1, 16):
            res = self.res["%02d" % index]
            self.return_transaction(res)

            self.assertEqual(
                round(self.radiogram_id.standard_price, 2), res["avg"],
                "operation: %02d - expected average - cost price is %s" % (
                    index, res["avg"]))
            self.assertEqual(
                round(self.radiogram_id.qty_available, 2), res["qty"],
                "Operation: %02d - Qty Available should be %s" % (
                    index, res["qty"]))
        return

    def test_01_accounting_booking(self):
        for index in range(1, 16):
            res = self.res["%02d" % index]
            self.return_transaction(res)

            aml_ids = self.aml_obj.search(
                [('product_id', '=', self.radiogram_id.id),
                 ('account_id', '=', self.val_id.id)])

            debit = sum([aml.debit for aml in aml_ids])
            credit = sum([aml.credit for aml in aml_ids])

            self.assertEqual(
                debit, res["debit"],
                "operation: %02d - expected debit %s" % (
                    index, res["debit"]))
            self.assertEqual(
                credit, res["credit"],
                "operation: %02d - expected credit %s" % (
                    index, res["credit"]))
        return

    def test_02_average_border_date(self):
        res_border = deepcopy(self.res)
        res_border.update(self.res_border)
        for index in range(1, 16):
            res = res_border["%02d" % index]
            if res.get('border'):
                date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.radiogram_id.write({'date_stock_account_border': date})
            self.return_transaction(res)

            self.assertEqual(
                round(self.radiogram_id.standard_price, 2), res["avg"],
                "operation: %02d - expected average - cost price is %s" % (
                    index, res["avg"]))
            self.assertEqual(
                round(self.radiogram_id.qty_available, 2), res["qty"],
                "Operation: %02d - Qty Available should be %s" % (
                    index, res["qty"]))
        return

    def test_02_booking_border_date(self):
        res_border = deepcopy(self.res)
        res_border.update(self.res_border)
        for index in range(1, 16):
            res = self.res["%02d" % index]
            # /!\ NOTE: Future anyone who wants to ask for this `IF` statement
            # in here. It was set because the data we want to test is dependant
            # on that `key`. And it can be set on the fly be reusing previous
            # demo data
            if res.get('border'):
                date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.radiogram_id.write({'date_stock_account_border': date})
            self.return_transaction(res)

            aml_ids = self.aml_obj.search(
                [('product_id', '=', self.radiogram_id.id),
                 ('account_id', '=', self.val_id.id)])

            debit = sum([aml.debit for aml in aml_ids])
            credit = sum([aml.credit for aml in aml_ids])

            self.assertEqual(
                debit, res["debit"],
                "operation: %02d - expected debit %s" % (
                    index, res["debit"]))
            self.assertEqual(
                credit, res["credit"],
                "operation: %02d - expected credit %s" % (
                    index, res["credit"]))
        return
