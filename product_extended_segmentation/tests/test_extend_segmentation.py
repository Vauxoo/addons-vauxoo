# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright 2015 Vauxoo
#    Author : Humberto Arocha <hbto@vauxoo.com>
#             Osval Reyes <osval@vauxoo.com>
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
from datetime import date


class TestExtendSegmentation(TransactionCase):

    def setUp(self):
        super(TestExtendSegmentation, self).setUp()
        self.prod_template = self.env['product.template']
        self.wizard = self.env['wizard.price']
        self.product_a_id = self.env.ref(
            'product_extended_segmentation.producto_a')
        self.product_b_id = self.env.ref(
            'product_extended_segmentation.producto_b')
        self.product_c_id = self.env.ref(
            'product_extended_segmentation.producto_c')
        self.product_d_id = self.env.ref(
            'product_extended_segmentation.producto_d')
        self.product_e_id = self.env.ref(
            'product_extended_segmentation.producto_e')

    def test_01_simple_costing_compute(self):
        tmpl_a_id = self.product_a_id.product_tmpl_id
        cost_a = self.product_a_id.standard_price + \
            tmpl_a_id.production_cost + \
            tmpl_a_id.material_cost + tmpl_a_id.landed_cost + \
            tmpl_a_id.subcontracting_cost

        tmpl_b_id = self.product_b_id.product_tmpl_id
        cost_b = self.product_b_id.standard_price + \
            tmpl_b_id.production_cost + \
            tmpl_b_id.material_cost + tmpl_b_id.landed_cost + \
            tmpl_b_id.subcontracting_cost

        tmpl_d_id = self.product_d_id.product_tmpl_id
        bom_d_id = tmpl_d_id.bom_ids[0]
        wc_line_ids = bom_d_id.routing_id.workcenter_lines
        routing_cost = sum([wcl_id.hour_nbr * wcl_id.workcenter_id.costs_hour
                            for wcl_id in wc_line_ids])

        self.assertTrue(routing_cost, "Routing Cost cannot be zero")

        computed_cost = tmpl_d_id._calc_price(bom=bom_d_id)
        self.assertEqual(computed_cost, cost_a + cost_b + routing_cost)

    def compute_price_from_wizard(self, product_id=False, real_time=False,
                                  recursive=False):
        pid = False
        if product_id._name == "product.template":
            tmpl_id = product_id
            pid = product_id.id
        elif product_id._name == "product.product":
            tmpl_id = product_id.product_tmpl_id
            pid = tmpl_id.id

        wizard_id = self.wizard.with_context({
            'active_id': pid,
            'active_model': 'product.template',
            'active_ids': [pid]
        }).create({
            'real_time_accounting': real_time,
            'recursive': recursive
        })

        wizard_id.compute_from_bom()
        return True

    def get_product_segmentation_costs(self, product_id=False):
        if product_id._name == "product.template":
            tmpl_id = product_id
        elif product_id._name == "product.product":
            tmpl_id = product_id.product_tmpl_id

        return {
            'std': tmpl_id.standard_price,
            'mat': tmpl_id.material_cost,
            'lan': tmpl_id.landed_cost,
            'sub': tmpl_id.subcontracting_cost,
            'pro': tmpl_id.production_cost
        }

    def test_02_BoM_D_cost_compute(self):
        tmpl_id = self.product_d_id.product_tmpl_id
        before_compute = tmpl_id.standard_price
        self.compute_price_from_wizard(self.product_d_id, False, True)

        self.assertTrue(before_compute != tmpl_id.standard_price)

        # Before compute cost: 50
        # After compute cost : 35 ( material=30, production=5 )
        self.assertTrue(before_compute - tmpl_id.standard_price == 15)

    def test_03_BoM_E_cost_compute(self):
        """
        Compute Product(E) without using recursive
        """
        tmpl_id = self.product_e_id.product_tmpl_id
        before_compute = tmpl_id.standard_price

        self.compute_price_from_wizard(self.product_e_id, False, True)

        # The cost changed
        self.assertTrue(before_compute != tmpl_id.standard_price)

        # Production cost should be: 15 = 10(E) + 5(D) production costs
        self.assertTrue(tmpl_id.production_cost == 15)

        # Material cost should be: 60 = 30(D)Material + 30(C)STD
        self.assertEqual(tmpl_id.material_cost, 60)
        self.assertEqual(tmpl_id.material_cost,
                         self.product_c_id.product_tmpl_id.standard_price +
                         self.product_d_id.product_tmpl_id.material_cost)

        # New Cost should be 75
        self.assertTrue(tmpl_id.standard_price == 75)

    def test_04_BoM_E_cost_compute_recursive(self):
        """
        Compute Product(E) using recursive calls
        """
        prod_d_before = self.get_product_segmentation_costs(self.product_d_id)
        prod_e_before = self.get_product_segmentation_costs(self.product_e_id)

        self.compute_price_from_wizard(self.product_e_id, True, True)

        # Get product costs segmentation after recompute cost have been done
        prod_d_after = self.get_product_segmentation_costs(self.product_d_id)
        prod_e_after = self.get_product_segmentation_costs(self.product_e_id)

        # The cost for product (D) have change decreasing in 15pts
        self.assertTrue(prod_d_before['std'] > prod_d_after['std'])
        self.assertTrue(prod_d_before['std'] - prod_d_after['std'], 15)
        self.assertEqual(prod_d_after['std'], 35)

        # Also the cost for product (E) have change in the same way with 5pts
        self.assertTrue(prod_e_before['std'] > prod_e_after['std'])
        self.assertEqual(prod_e_before['std'] - prod_e_after['std'], 5)
        self.assertEqual(prod_e_after['std'], 75)

        # For product E cost should  be:
        #   - Material   : 60 = 10(A) + 20(B) + 30(C)
        self.assertEqual(prod_e_after['mat'], 60)
        #   - Production : 15 = 10(E) + 5(D)
        self.assertEqual(prod_e_after['pro'], 15)

    def test_05_BoM_E_increasing_cost(self):
        def set_starting_cost(product_id, cost):
            product_id.write({
                'standard_price': cost
            })
            quant_id = self.env['stock.quant'].search([
                ('product_id', '=', product_id.id)
            ])
            quant_id.write({
                'cost': cost,
                'material_cost': cost,
                'inventory_value': quant_id.qty * cost
            })

        set_starting_cost(self.product_b_id, 30)
        set_starting_cost(self.product_c_id, 35)

        prod_d_before = self.get_product_segmentation_costs(self.product_d_id)
        prod_e_before = self.get_product_segmentation_costs(self.product_e_id)

        self.compute_price_from_wizard(self.product_e_id, True, True)

        # Get product costs segmentation after recompute cost have been done
        prod_d_after = self.get_product_segmentation_costs(self.product_d_id)
        prod_e_after = self.get_product_segmentation_costs(self.product_e_id)

        # The cost for product (D) have increased in 10pts
        self.assertTrue(prod_e_before['std'] < prod_e_after['std'])
        self.assertEqual(prod_e_after['std'] - prod_e_before['std'], 10)
        self.assertEqual(prod_e_after['std'], 90)
