# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright 2016 Vauxoo
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


class TestProductSegmentation(TransactionCase):

    def setUp(self):
        super(TestProductSegmentation, self).setUp()
        self.prod_e_id = self.env.ref(
            'product_extended_segmentation.producto_e')
        self.env.ref('base.main_company').\
            write({'std_price_neg_threshold': 100})
        self.wizard = self.env['wizard.price']

        # use mrp_workcenter_segmentation routing defined for E production
        self.env.ref('product_extended_segmentation.bom_product_e').write({
            'routing_id': self.ref('mrp_workcenter_segmentation.'
                                   'routing_segmentation_e_product')
        })

    def create_update_wizard(self, tmpl_id, do_recursive, do_update):
        self.wizard.with_context({
            'active_model': tmpl_id._name,
            'active_id': tmpl_id.id,
            'active_ids': tmpl_id.ids,
        }).create({
            'recursive': do_recursive,
            'update_avg_costs': do_update
        }).compute_from_bom()

    def test_01_product_update_with_production_sgmnts(self):
        self.create_update_wizard(self.prod_e_id.product_tmpl_id,
                                  False, True)
        self.assertEqual(self.prod_e_id.standard_price, 110)
        # 30(C) + 50(D)
        self.assertEqual(self.prod_e_id.material_cost, 80)
        self.assertEqual(self.prod_e_id.landed_cost, 0)
        # 15(E)
        self.assertEqual(self.prod_e_id.production_cost, 15)
        # 15(E)
        self.assertEqual(self.prod_e_id.subcontracting_cost, 15)

    def test_02_product_update_with_production_sgmnts_recursive(self):
        self.create_update_wizard(self.prod_e_id.product_tmpl_id,
                                  True, True)
        self.assertEqual(self.prod_e_id.standard_price, 95)
        # A(10) + B(20) + C(30)
        self.assertEqual(self.prod_e_id.material_cost, 60)
        self.assertEqual(self.prod_e_id.landed_cost, 0)
        # 20 = 15(E) + 5(D)
        self.assertEqual(self.prod_e_id.production_cost, 20)
        # 15(E)
        self.assertEqual(self.prod_e_id.subcontracting_cost, 15)
