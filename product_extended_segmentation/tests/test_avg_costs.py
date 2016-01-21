# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright 2016 Vauxoo
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
import pdb
SEGMENTATION_COST = [
    'landed_cost',
    'subcontracting_cost',
    'material_cost',
    'production_cost',
]


class TestAvgCosts(TransactionCase):

    def setUp(self):
        super(TestAvgCosts, self).setUp()
        self.prod_template = self.env['product.template']
        self.wizard = self.env['wizard.price']
        self.prod_a_id = self.env.ref(
            'product_extended_segmentation.producto_a')
        self.prod_b_id = self.env.ref(
            'product_extended_segmentation.producto_b')
        self.prod_c_id = self.env.ref(
            'product_extended_segmentation.producto_c')
        self.prod_d_id = self.env.ref(
            'product_extended_segmentation.producto_d')
        self.prod_e_id = self.env.ref(
            'product_extended_segmentation.producto_e')
        self.product_ids = [self.prod_a_id,
                            self.prod_b_id,
                            self.prod_c_id]

    def get_store_product_values(self, product_ids):
        vals = {}
        for product_id in product_ids:
            sgmnts = {}
            for fieldname in SEGMENTATION_COST:
                val = getattr(product_id, fieldname)
                if val:
                    sgmnts[fieldname] = val
            if len(sgmnts):
                vals[product_id.name] = sgmnts.copy()
        return vals

    def create_wizard(self, product_tmpl_id, recursive,
                      real_time_accounting, update_avg_costs):
        wizard_id = self.wizard.with_context({
            'active_model': product_tmpl_id._name,
            'active_id': product_tmpl_id.id,
            'active_ids': product_tmpl_id.ids,
        }).create({
            'recursive': recursive,
            'real_time_accounting': real_time_accounting,
            'update_avg_costs': update_avg_costs
        })

        wizard_id.compute_from_bom()

        return wizard_id

    def test_01_avg_products_costs(self):
        res = {}
        res = self.get_store_product_values(
            self.product_ids)

        # check initial values for avg products
        self.assertEqual(res, {})

        wizard_id = self.create_wizard(
            self.prod_e_id.product_tmpl_id, True, False, True)
        res = self.get_store_product_values(
            self.product_ids)

        # check updated segment costs for avg products after wizard execution
        self.assertEqual(res['producto_a']['material_cost'], 10)
        self.assertEqual(res['producto_b']['material_cost'], 20)
        self.assertEqual(res['producto_c']['material_cost'], 30)
