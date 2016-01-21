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

    def check_wizard_values(self, product_id, vals):
        # check before wizard
        self.assertEqual(product_id.standard_price, vals['before'],
                         'Standard Price for {0} should be {1}'.
                         format(product_id.name, vals['before']))
        wizard_id = self.create_wizard(product_id)[0]
        self.assertEqual(wizard_id.recursive, False,
                         'WizardPrice recursive check should be unchecked'
                         'by default')
        cost = self.get_product_cost(
            wizard_id.info_field, product_id.id)
        # check what a wizard returns as default value
        self.assertEqual(cost, vals['default'],
                         'Non-recursive cost valuation for {0} should be {1}'.
                         format(product_id.name, vals['default']))

        res = wizard_id.onchange_recursive(True)['value']
        cost = self.get_product_cost(res['info_field'], product_id.id)

        # check what recursive returns
        self.assertEqual(cost, vals['after'],
                         'Recursive cost for {0} should be keep at {1}'.
                         format(product_id.name, vals['after']))

    def test_01_test_wizard_onchange_recursive(self):
        vals = {
            'before': 50,
            'default': 35,
            'after': 35
        }
        self.check_wizard_values(self.producto_d_id, vals)
        vals = {
            'before': 80,
            'default': 40,
            'after': 75
        }
        self.check_wizard_values(self.producto_e_id, vals)
