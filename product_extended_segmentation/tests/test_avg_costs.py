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
SEGMENTATION_COST = [
    'landed_cost',
    'subcontracting_cost',
    'material_cost',
    'production_cost',
]


class TestAvgCosts(TransactionCase):

    def setUp(self):
        super(TestAvgCosts, self).setUp()
        self.product = self.env['product.product']
        self.prod_template = self.env['product.template']
        self.wizard = self.env['wizard.price']
        self.company_id = self.env.user.company_id
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

    def test_00_cron_methods(self):
        sgmnts = {}
        self.company_id.write({'std_price_neg_threshold': 0})
        sgmnts['before'] = [getattr(self.prod_e_id, fieldname)
                            for fieldname in SEGMENTATION_COST]
        self.assertEqual(sum(sgmnts['before']), 0.0, 'sgmnts should be 0.0')
        self.product.update_material_cost_on_zero_segmentation()
        self.prod_e_id.refresh()
        sgmnts['after'] = [getattr(self.prod_e_id, fieldname)
                           for fieldname in SEGMENTATION_COST]
        self.assertEqual(sum(sgmnts['after']), 80.0, 'Segments should be 80.0')

    def get_store_product_values(self, product_ids):
        vals = {}
        for brw in product_ids:
            vals[brw.name] = {}
            for fieldname in SEGMENTATION_COST:
                vals[brw.name][fieldname] = getattr(brw, fieldname)
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
        self.assertNotEqual(res, {})

        self.create_wizard(self.prod_e_id.product_tmpl_id, True, False, True)
        res = self.get_store_product_values(self.product_ids)

        # check updated segment costs for avg products after wizard execution
        # /!\ NOTE: At this moment Business logic has changed and AVG products
        # are no longer updated from Wizard that updates STD product costs
        self.assertEqual(res['producto_a']['material_cost'], 0)
        self.assertEqual(res['producto_b']['material_cost'], 0)
        self.assertEqual(res['producto_c']['material_cost'], 0)

    def test_02_compute_price_with_real_bom(self):
        template_id = self.prod_e_id.product_tmpl_id
        self.prod_d_id.write({'cost_method': 'real'})
        res = self.env['product.template'].compute_price(
            product_ids=False, recursive=True,  real_time_accounting=False,
            template_ids=[template_id.id], test=True)
        self.assertEqual(str(res),
                         '{{{0}: 75.0}}'.format(str(template_id.id)))

    def test_03_write_real_cost_product_price_using_wizard(self):
        template_id = self.prod_e_id.product_tmpl_id
        self.prod_d_id.write({'cost_method': 'real'})
        old_price = self.prod_d_id.standard_price
        res = self.env['product.template'].compute_price(
            product_ids=False, recursive=True,  real_time_accounting=True,
            template_ids=[template_id.id], test=False)
        self.assertNotEqual(old_price, self.prod_d_id.standard_price)
