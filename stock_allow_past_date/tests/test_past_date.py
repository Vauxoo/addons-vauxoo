# -*- coding: utf-8 -*-
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: Katherine Zaoral <kathy@vauxoo.com>
#    planned by: Nhomar Hernandez <nhomar@vauxoo.com>
############################################################################

from openerp.tests import common
from datetime import datetime
from dateutil.relativedelta import relativedelta


class TestPickingDate(common.TransactionCase):

    """Test that can create a picking with the current date of a past date,
    validate then and generate a move and quant with that past date instead the
    current date.
    """

    def setUp(self):
        super(TestPickingDate, self).setUp()
        self.product_obj = self.env['product.product']
        self.picking_obj = self.env['stock.picking']
        self.move_obj = self.env['stock.move']
        self.quant_obj = self.env['stock.quant']

        self.source_location = self.ref('stock.stock_location_stock')
        self.dest_location = self.ref('stock.stock_location_customers')
        self.picking_type = self.ref('stock.picking_type_out')

        # Get products
        products = self.product_obj.search([])
        products_w_quants = self.quant_obj.search([]).mapped('product_id')
        products_wo_quants = products - products_w_quants

        self.product_wo_quant = products_wo_quants[0]
        self.product_w_quant = products_w_quants[0]

    def test_01_current_date_wo_quants(self):
        """Create picking with current date for a product without quants.
        Generate move/quant with the same date.
        """
        picking_date = datetime(2016, 6, 8, 12, 0)
        self._test_picking_date(picking_date, self.product_wo_quant)

    def test_02_current_date_w_quants(self):
        """Create picking with current date for a product with quants.
        Generate move/quant with the same date.
        """
        picking_date = datetime(2016, 6, 8, 12, 0)
        self._test_picking_date(picking_date, self.product_w_quant)

    def test_03_past_date_wo_quants(self):
        """Create picking with past date for a product without quants.
        Generate move/quant with the same date.
        """
        picking_date = datetime(2016, 6, 8, 12, 0) - relativedelta(days=15)
        self._test_picking_date(picking_date, self.product_wo_quant)

    def test_04_past_date_w_quants(self):
        """Create picking with past date for a product with quants.
        Generate move/quant with the same date.
        In this case the quant must to do with the current date.
        """
        picking_date = datetime(2016, 6, 8, 12, 0) - relativedelta(days=15)
        diff_day = self.get_day(datetime(2016, 6, 8, 12, 0))
        self._test_picking_date(picking_date, self.product_w_quant, diff_day)

    def _test_picking_date(self, picking_date, product, diff_day=None):
        """Create a picking with x date
        Generate move/quant with same date.
        Check the dates
        """
        picking_day = picking_date.strftime('%Y-%m-%d')
        picking_date = picking_date.strftime('%Y-%m-%d %H:%M:%S')

        picking = self.picking_obj.create({
            'name': 'Picking Past Date',
            'date': picking_date,
            'min_date': picking_date,
            'picking_type_id': self.picking_type,
        })
        self.assertTrue(picking)

        # Create Move and associated to picking
        move = self.move_obj.create({
            'picking_id': picking.id,
            'name': 'Move Past Date',
            'product_id': product.id,
            'product_uom': product.uom_id.id,
            'product_uom_qty': 500,
            'location_id': self.source_location,
            'location_dest_id': self.dest_location,
            'date': picking_date,
        })

        self.assertTrue(move)
        self.assertEqual(picking.move_lines, move)

        # Confirm Picking
        picking.with_context({'allow_past_date_quants': True}).action_confirm()

        # Validate Picking
        picking.with_context({'allow_past_date_quants': True}).do_transfer()
        self.assertEqual(picking.state, 'done')

        # Check move dates
        self.assertEqual(move.state, 'done')
        move_day = self.get_day(move.date)
        self.assertEqual(move_day, diff_day or picking_day)

        # Get quant day
        quants = move.quant_ids
        quant_in_date = quants.mapped('in_date')
        self.assertTrue(len(quant_in_date), 1)
        quant_in_day = self.get_day(quant_in_date[0])

        # Check quant dates
        self.assertEqual(quant_in_day, diff_day or picking_day)

    def get_day(self, long_date):
        """ Return the day str of a date.
        """
        if isinstance(long_date, str):
            day = datetime.strptime(
                long_date, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
        else:
            day = long_date.strftime('%Y-%m-%d')
        return day
