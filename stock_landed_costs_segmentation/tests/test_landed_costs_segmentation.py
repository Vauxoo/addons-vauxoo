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

        self.picking_id = self.env.ref(
            'stock_landed_costs_segmentation.picking_01')
        self.product_freight_id = self.env.ref(
            'stock_landed_costs_average'
            '.service_standard_periodic_landed_cost_1')
        self.product_insurance_id = self.env.ref(
            'stock_landed_costs_average'
            '.service_standard_periodic_landed_cost_2')
        pass

    def do_picking(self):
        transfer_details = self.env['stock.transfer_details']
        self.picking_id.action_confirm()
        wizard_id = self.wizard.create({
            'picking_id': self.picking_id.id,
        })

        for move_id in self.picking_id.move_lines:
            self.wizard_item.create({
                'transfer_id': wizard_id.id,
                'product_id': move_id.product_id.id,
                'quantity': move_id.product_qty,
                'sourceloc_id': move_id.location_id.id,
                'destinationloc_id': move_id.location_dest_id.id,
                'product_uom_id': move_id.product_uom.id,
            })

        wizard_id.do_detailed_transfer()
        self.assertEqual(self.picking_id.state, 'done')

    def test_01_segmentations(self):
        self.do_picking()
        slc_id = self.slc.create({
            'account_journal_id': self.ref(
                'stock_landed_costs_average.stock_landed_cost_1'),
            'picking_ids': [(4, self.picking_id.id), ],
            'cost_lines': [
                (0, 0, {
                    'product_id': self.product_insurance_id.id,
                    'split_method': 'by_quantity',
                    'price_unit': 150,
                    'segmentation_cost': 'subcontracting_cost',
                }),
                (0, 0, {
                    'product_id': self.product_freight_id.id,
                    'split_method': 'by_quantity',
                    'price_unit': 180,
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

        for quant in self.picking_id.move_lines.quant_ids:
            self.assertEqual(quant.landed_cost, 50,
                             'Landed Cost should be 50')
            self.assertEqual(quant.subcontracting_cost, 60,
                             'Landed Cost should be 60')
