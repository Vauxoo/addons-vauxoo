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
from odoo.addons.mrp.tests.common import TestMrpCommon


class TestAccountMoveLineProduction(TestMrpCommon):

    def setUp(self):
        super(TestAccountMoveLineProduction, self).setUp()
        self.production_a = self.env.ref(
            'account_move_line_production.production_a')

    def produce(self, production_id=False):

        self.wizard_id = self.env['mrp.product.produce'].sudo(
            self.user_mrp_user).with_context({
                'active_id': production_id.id,
                'active_ids': [production_id.id],
        }).create({
            'product_qty': 1.0,
        })
        self.wizard_id.do_produce()
        production_id.button_mark_done()
        return True

    def test_01(self):
        self.assertEqual(self.production_a.state, 'confirmed')
        self.produce(self.production_a)
        self.assertEqual(self.production_a.state, 'done')
        self.assertTrue(self.production_a.aml_production_ids)
