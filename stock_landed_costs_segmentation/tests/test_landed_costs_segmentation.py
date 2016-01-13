# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright 2015 Vauxoo
#    Author : Osval Reyes <osval@vauxoo.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.tests.common import TransactionCase


class TestLandedCostsSegmentation(TransactionCase):

    def setUp(self):
        super(TestLandedCostsSegmentation, self).setUp()
        self.move = self.env['stock.move']
        self.slc = self.env['stock.landed.cost']
        self.wizard = self.env['stock.transfer_details']
        self.wizard_item = self.env['stock.transfer_details_items']

        self.picking_01_id = self.env.ref(
            'stock_landed_costs_segmentation.po_01').picking_ids[0]
        self.picking_02_id = self.env.ref(
            'stock_landed_costs_segmentation.po_02').picking_ids[0]
        self.product_freight_id = self.env.ref(
            'stock_landed_costs_average'
            '.service_standard_periodic_landed_cost_1')
        self.product_insurance_id = self.env.ref(
            'stock_landed_costs_average'
            '.service_standard_periodic_landed_cost_2')

        self.product_01 = self.env.ref(
            'stock_landed_costs_segmentation.product_std_01')

        self.product_02 = self.env.ref(
            'stock_landed_costs_segmentation.product_avg_01')

        self.product_03 = self.env.ref(
            'stock_landed_costs_segmentation.product_real_01')

    def do_picking(self, picking_id=False):
        picking_id.action_confirm()
        wizard_id = self.wizard.create({
            'picking_id': picking_id.id,
        })

        for move_id in picking_id.move_lines:
            self.wizard_item.create({
                'transfer_id': wizard_id.id,
                'product_id': move_id.product_id.id,
                'quantity': move_id.product_qty,
                'sourceloc_id': move_id.location_id.id,
                'destinationloc_id': move_id.location_dest_id.id,
                'product_uom_id': move_id.product_uom.id,
            })

        wizard_id.do_detailed_transfer()
        self.assertEqual(picking_id.state, 'done')

    def create_and_validate_landed_costs(self, picking_id=False,
                                         insurance_cost=15000,
                                         freight_cost=18000):
        slc_id = self.slc.create({
            'account_journal_id': self.ref(
                'stock_landed_costs_average.stock_landed_cost_1'),
            'picking_ids': [(4, picking_id.id), ],
            'cost_lines': [
                (0, 0, {
                    'name': 'insurance',
                    'product_id': self.product_insurance_id.id,
                    'split_method': 'by_quantity',
                    'price_unit': insurance_cost,
                    'segmentation_cost': 'subcontracting_cost',
                }),
                (0, 0, {
                    'name': 'freight',
                    'product_id': self.product_freight_id.id,
                    'split_method': 'by_quantity',
                    'price_unit': freight_cost,
                    'segmentation_cost': 'landed_cost',
                }),
            ]
        })

        self.assertEqual(len(slc_id.picking_ids), 1)
        self.assertEqual(len(slc_id.cost_lines), 2)

        # compute and check landed costs
        slc_id.compute_landed_cost()
        self.assertEqual(len(slc_id.valuation_adjustment_lines), 6)

        # validate landed costs
        slc_id.button_validate()

        return slc_id

    def get_quant(self, picking_id=False, product_id=False):
        for quant_id in picking_id.mapped('move_lines.quant_ids'):
            if quant_id.product_id == product_id:
                return quant_id

    def test_01_segmentations(self):
        # check initial product costs
        self.assertEqual(self.product_01.standard_price, 100)
        self.assertEqual(self.product_02.standard_price, 100)
        self.assertEqual(self.product_03.standard_price, 100)

        # make incoming stock movements
        self.do_picking(self.picking_01_id)
        self.create_and_validate_landed_costs(self.picking_01_id,
                                              insurance_cost=15000,
                                              freight_cost=18000)

        self.assertEqual(self.product_02.material_cost, 100)
        self.assertEqual(self.product_02.landed_cost, 60)
        self.assertEqual(self.product_02.production_cost, 0)
        self.assertEqual(self.product_02.subcontracting_cost, 50)
        self.assertEqual(self.product_02.standard_price, 210)

        # check inventory valuations
        self.assertEqual(sorted(self.picking_01_id.mapped(
            'move_lines.quant_ids.inventory_value')),
            [10000, 21000, 21000],
            "Inventory valuations from picking #1 doesn't match")

        product_std_quant_id = self.get_quant(self.picking_01_id,
                                              self.product_01)
        product_avg_quant_id = self.get_quant(self.picking_01_id,
                                              self.product_02)
        product_real_quant_id = self.get_quant(self.picking_01_id,
                                               self.product_03)

        # check product costs
        self.assertEqual(self.product_01.standard_price, 100)
        self.assertEqual(self.product_02.standard_price, 210)
        self.assertEqual(self.product_03.standard_price, 100)

        # check quant costs
        self.assertEqual(product_std_quant_id.cost, 100)
        self.assertEqual(product_avg_quant_id.cost, 210)
        self.assertEqual(product_real_quant_id.cost, 210)

        # check segmentation costs (M+L+P+S)
        self.assertEqual(product_std_quant_id.segmentation_cost, 210)
        self.assertEqual(product_avg_quant_id.segmentation_cost, 210)
        self.assertEqual(product_real_quant_id.segmentation_cost, 210)

        # check splitted costs
        for quant in self.picking_01_id.mapped('move_lines.quant_ids'):
            self.assertEqual(quant.landed_cost, 60,
                             'Landed Cost should be 60')
            self.assertEqual(quant.subcontracting_cost, 50,
                             'Subcontrating Cost should be 50')
            self.assertEqual(quant.material_cost, 100,
                             'Material Cost should be 100')

        # Receive products
        self.do_picking(self.picking_02_id)
        self.create_and_validate_landed_costs(self.picking_02_id,
                                              insurance_cost=31500,
                                              freight_cost=9000)

        # check inventory valuations
        self.assertEqual(sorted(self.picking_02_id.mapped(
            'move_lines.quant_ids.inventory_value')),
            [15000, 28500, 39600],
            "Inventory valuations from picking #2 doesn't match")

        product_std_quant_id = self.get_quant(self.picking_02_id,
                                              self.product_01)
        product_avg_quant_id = self.get_quant(self.picking_02_id,
                                              self.product_02)
        product_real_quant_id = self.get_quant(self.picking_02_id,
                                               self.product_03)

        # check quant costs
        self.assertEqual(product_std_quant_id.cost, 100)
        self.assertEqual(product_avg_quant_id.cost, 300)
        self.assertEqual(product_real_quant_id.cost, 190)

        # check segmentation costs
        self.assertEqual(product_std_quant_id.segmentation_cost, 190)
        self.assertEqual(product_avg_quant_id.segmentation_cost, 300)
        self.assertEqual(product_real_quant_id.segmentation_cost, 190)

        self.assertEqual(product_std_quant_id.material_cost, 100)
        self.assertEqual(product_avg_quant_id.material_cost, 210)
        self.assertEqual(product_real_quant_id.material_cost, 100)

        self.assertEqual(product_std_quant_id.landed_cost, 20)
        self.assertEqual(product_avg_quant_id.landed_cost, 20)
        self.assertEqual(product_real_quant_id.landed_cost, 20)

        self.assertEqual(product_std_quant_id.subcontracting_cost, 70)
        self.assertEqual(product_avg_quant_id.subcontracting_cost, 70)
        self.assertEqual(product_real_quant_id.subcontracting_cost, 70)

        self.assertEqual(self.product_02.material_cost, 166)
        self.assertEqual(self.product_02.landed_cost, 36)
        self.assertEqual(self.product_02.production_cost, 0)
        self.assertEqual(self.product_02.subcontracting_cost, 64)
        self.assertEqual(self.product_02.standard_price, 264)

        # check product costs
        self.assertEqual(self.product_01.standard_price, 100)
        self.assertEqual(self.product_02.standard_price, 264)
        self.assertEqual(self.product_03.standard_price, 100)
