# -*- coding: utf-8 -*-

from openerp.tests.common import TransactionCase
from openerp.exceptions import except_orm, Warning as UserError


class TestBasics(TransactionCase):

    def setUp(self):
        super(TestBasics, self).setUp()
        self.company_id = self.env.ref('base.main_company')
        self.slc = self.env['stock.landed.cost']
        self.slc_id = self.env.ref('stock_landed_costs_average.slc_02')
        self.vals = {
            'gain_acct_id':
            self.company_id.gain_inventory_deviation_account_id.id,
            'loss_acct_id':
            self.company_id.loss_inventory_deviation_account_id.id
        }

    def toggle_deviation_accts(self, write):
        gain_acct_id = False
        loss_acct_id = False
        if write:
            gain_acct_id = self.vals['gain_acct_id']
            loss_acct_id = self.vals['loss_acct_id']

        self.company_id.sudo().write({
            'gain_inventory_deviation_account_id': gain_acct_id,
            'loss_inventory_deviation_account_id': loss_acct_id
        })
        self.assertEquals(
            self.company_id.gain_inventory_deviation_account_id.id,
            gain_acct_id)
        self.assertEquals(
            self.company_id.loss_inventory_deviation_account_id.id,
            loss_acct_id)

    def test_01_without_deviation_account(self):
        self.toggle_deviation_accts(write=False)
        self.slc_id.compute_landed_cost()
        msg_error = 'Please configure Gain & Loss Inventory.*'
        with self.assertRaisesRegexp(except_orm, msg_error):
            self.slc_id.button_validate()

    def test_02_revalidate(self):
        self.assertEquals(self.slc_id.state, 'draft')
        self.slc_id.compute_landed_cost()
        self.slc_id.button_validate()
        self.assertTrue(self.slc_id.state != 'draft')

        msg_error = 'Only draft landed costs can be validated'
        with self.assertRaisesRegexp(UserError, msg_error):
            self.slc_id.button_validate()

    def test_03_validate_without_adjustment_lines(self):
        msg_error = 'You cannot validate a landed cost which has no valid.*'
        with self.assertRaisesRegexp(UserError, msg_error):
            self.slc_id.button_validate()

    def test_04_create_account_entries_positive(self):
        self.assertEquals(self.slc_id.state, 'draft')
        self.slc_id.compute_landed_cost()
        self.slc_id.button_validate()
        self.assertEquals(
            self.slc_id.valuation_adjustment_lines[0].additional_landed_cost,
            100)

    def test_05_create_account_entries_negative(self):
        self.assertEquals(self.slc_id.state, 'draft')
        self.slc_id.cost_lines[0].write({
            'price_unit': -100
        })
        self.slc_id.compute_landed_cost()
        self.slc_id.button_validate()
        self.assertEquals(
            self.slc_id.valuation_adjustment_lines[0].additional_landed_cost,
            -100)

    def test_06_real_time_valuations(self):
        self.assertEqual(self.slc_id.get_valuation_lines(), [])
        for picking_id in self.slc_id.picking_ids:
            for move_id in picking_id.move_lines:
                move_id.product_id.write({'valuation': 'manual_periodic'})
        picking_ids = [pid.id for pid in self.slc_id.picking_ids]
        msg_error = 'The selected picking does not contain any move that.*'
        with self.assertRaisesRegexp(except_orm, msg_error):
            self.slc_id.get_valuation_lines(picking_ids)
