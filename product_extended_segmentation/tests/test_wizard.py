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
from openerp.tools.safe_eval import safe_eval


class TestWizard(TransactionCase):

    def setUp(self):
        super(TestWizard, self).setUp()
        self.prod_template = self.env['product.template']
        self.wizard = self.env['wizard.price']
        self.company_id = self.env.user.company_id
        self.producto_d_id = self.env.ref(
            'product_extended_segmentation.producto_d').product_tmpl_id
        self.producto_e_id = self.env.ref(
            'product_extended_segmentation.producto_e').product_tmpl_id

    def create_wizard(self, product_tmpl_id, recursive=False,
                      real_time_accounting=False, update_avg_costs=False):
        return self.wizard.with_context({
            'active_model': product_tmpl_id._name,
            'active_id': product_tmpl_id.id,
            'active_ids': product_tmpl_id.ids,
            'update_avg_costs': recursive and update_avg_costs,
        }).create({
            'recursive': recursive,
            'real_time_accounting': real_time_accounting,
            'update_avg_costs': recursive and update_avg_costs,
        })

    def get_product_cost(self, info_field, product_tmpl_id):
        return safe_eval(info_field)[product_tmpl_id]

    def check_default_cost(self, product_id, value):
        wizard_id = self.create_wizard(product_id)[0]
        cost = self.get_product_cost(wizard_id.info_field, product_id.id)
        self.assertEqual(cost, value, 'Default wizard value for {0} '
                         'should be {1}'.format(product_id.name, value))

    def test_00_test_wizard_defaults(self):
        wizard_id = self.create_wizard(self.producto_d_id)[0]
        self.assertEqual(wizard_id.recursive, False,
                         'Recursive check should be unchecked by default')
        self.check_default_cost(self.producto_d_id, 35)
        self.check_default_cost(self.producto_e_id, 90)

    def test_01_test_threshold_no_update(self):
        self.company_id.write({'std_price_neg_threshold': 0})
        # ============================
        # ==== PRODUCT D
        # ============================
        self.assertEqual(self.producto_d_id.standard_price, 50,
                         'Standard Price for D should be 50')
        wizard_id = self.create_wizard(
            self.producto_d_id, recursive=True, update_avg_costs=True)
        wizard_id.compute_from_bom()

        # check what recursive returns
        self.assertEqual(self.producto_d_id.standard_price, 50,
                         'Recursive cost for D should be keep at 50')
        # check production_cost
        self.assertEqual(self.producto_d_id.production_cost, 5,
                         'Production Cost for D should be 5')

        # ============================
        # ==== PRODUCT E
        # ============================
        self.assertEqual(self.producto_e_id.standard_price, 80,
                         'Standard Price for {0} should be {1}'.
                         format(self.producto_e_id.name, 80))
        wizard_id = self.create_wizard(
            self.producto_e_id, recursive=True, update_avg_costs=True)
        wizard_id.compute_from_bom()

        # check what recursive returns
        self.assertEqual(self.producto_e_id.standard_price, 80,
                         'Recursive cost for E should be keep at 80')

        # check production_cost
        self.assertEqual(self.producto_e_id.production_cost, 15,
                         'Production Cost for E should be 15')

    def test_01_test_threshold_th_30_update(self):
        self.company_id.write({'std_price_neg_threshold': -30})
        # ============================
        # ==== PRODUCT D
        # ============================
        self.assertEqual(self.producto_d_id.standard_price, 50,
                         'Standard Price for D should be 50')
        wizard_id = self.create_wizard(
            self.producto_d_id, recursive=True, update_avg_costs=True)
        wizard_id.compute_from_bom()

        # check what recursive returns
        self.assertEqual(self.producto_d_id.standard_price, 35,
                         'Recursive cost for D should be keep at 35')
        # check production_cost
        self.assertEqual(self.producto_d_id.production_cost, 5,
                         'Production Cost for D should be 5')

        # ============================
        # ==== PRODUCT E
        # ============================
        self.assertEqual(self.producto_e_id.standard_price, 80,
                         'Standard Price for E should be 80')
        wizard_id = self.create_wizard(
            self.producto_e_id, recursive=True, update_avg_costs=True)
        wizard_id.compute_from_bom()

        # check what recursive returns
        self.assertEqual(self.producto_e_id.standard_price, 75,
                         'Recursive cost for E should be keep at 75')
        # check production_cost
        self.assertEqual(self.producto_e_id.production_cost, 15,
                         'Production Cost for E should be 15')
