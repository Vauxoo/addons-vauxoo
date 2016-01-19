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


class TestWizard(TransactionCase):

    def setUp(self):
        super(TestWizard, self).setUp()
        self.prod_template = self.env['product.template']
        self.wizard = self.env['wizard.price']
        self.producto_d_id = self.env.ref(
            'product_extended_segmentation.producto_d').product_tmpl_id
        self.producto_e_id = self.env.ref(
            'product_extended_segmentation.producto_e').product_tmpl_id

    def create_wizard(self, product_tmpl_id):
        return self.wizard.with_context({
            'active_model': product_tmpl_id._name,
            'active_id': product_tmpl_id.id,
            'active_ids': product_tmpl_id.ids,
        }).create({})

    def get_product_cost(self, info_field, product_tmpl_id):
        return eval(info_field)[product_tmpl_id]

    def test_01_test_wizard_onchange_recursive(self):
        wizard_id = self.create_wizard(self.producto_d_id)[0]
        self.assertEqual(wizard_id.recursive, False,
                         'WizardPrice recursive check should be unchecked'
                         'by default')
        cost = self.get_product_cost(
            wizard_id.info_field, self.producto_d_id.id)
        self.assertEqual(cost, 35, 'Non-recursive cost valuation should be 35')

        wizard_id.recursive = True

        cost = self.get_product_cost(
            wizard_id.info_field, self.producto_d_id.id)
        self.assertEqual(cost, 35, 'Recursive cost for D should be keep at 35')

        wizard_id = self.create_wizard(self.producto_e_id)[0]
        self.assertEqual(wizard_id.recursive, False,
                         'WizardPrice recursive check should be unchecked'
                         'by default')
        cost = self.get_product_cost(
            wizard_id.info_field, self.producto_e_id.id)
        self.assertEqual(cost, 40, 'Non-recursive cost for E should be 40')

        res = wizard_id.onchange_recursive(True)['value']

        cost = self.get_product_cost(res['info_field'], self.producto_e_id.id)
        self.assertEqual(cost, 75, 'Recursive cost for E should be up to 75')
