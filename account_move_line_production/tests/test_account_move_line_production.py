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


class TestAccountMoveLineProduction(TransactionCase):

    def setUp(self):
        super(TestAccountMoveLineProduction, self).setUp()
        self.production_a = self.env.ref(
            'account_move_line_production.production_a')

    def produce(self, production_id=False):
        self.wizard_id = self.env['mrp.product.produce'].with_context({
            'active_id': production_id.id
        }).create({})
        values = self.env['mrp.product.produce'].with_context({
            'active_id': production_id.id
        }).on_change_qty(self.wizard_id.id, 1)

        values = values['value']['consume_lines']

        for val in values:
            val = val[2]
            val['produce_id'] = self.wizard_id.id
            self.env['mrp.product.produce.line'].create(val)

        self.wizard_id.do_produce()
        return True

    def test_01(self):
        self.assertEqual(self.production_a.state, 'in_production')

        self.produce(self.production_a)
        self.assertEqual(self.production_a.state, 'done')

        self.assertTrue(self.production_a.aml_production_ids)
