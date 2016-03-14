# coding: utf-8
# © 2015 Vauxoo - http://www.vauxoo.com
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# info Vauxoo (info@vauxoo.com)
# coded by: karen@vauxoo.com
# planned by: hbto@vauxoo.com

from openerp.tests.common import TransactionCase


class TestWorkcenterSegmentation(TransactionCase):

    # Pseudo-constructor method of the setUp test.
    def setUp(self):
        super(TestWorkcenterSegmentation, self).setUp()
        # Define required global variables.
        self.account_stock_valuation = self.ref('account.stk')
        self.account_cost = self.ref(
            'mrp_workcenter_account_move.rev_production_cost_account')
        self.account_deviation = self.ref(
            'stock_deviation_account.rev_inventory_deviation_account')
        self.mrp_production_d = self.env.ref(
            'mrp_workcenter_segmentation.'
            'mrp_production_segmentation_d_product')
        self.mrp_production_e = self.env.ref(
            'mrp_workcenter_segmentation.'
            'mrp_production_segmentation_e_product')
        self.wip_account = self.env.ref(
            'mrp_workcenter_account_move.rev_work_in_process')
        self.wizard = self.env['mrp.product.produce']
        self.wizard_line = self.env['mrp.product.produce.line']
        self.quant = self.env['stock.quant']
        self.location = self.env['stock.location']
        location_id = self.location.search([('name', '=', 'Production')])
        location_id.write({
            'valuation_in_account_id': self.wip_account.id,
            'valuation_out_account_id': self.wip_account.id
        })

    def produce_product(self, production_id, qties):
        # Confirm the mrp production d.
        production_id.signal_workflow('button_confirm')
        self.assertEqual(production_id.state, 'confirmed')

        production_id.action_assign()
        self.assertEqual(production_id.state, 'ready')

        # Begin mrp production.
        production_id.signal_workflow('button_produce')
        self.assertEqual(production_id.state, 'in_production')

        # Consumption and finish production.
        for qty in qties:
            self.create_wizard(production_id, qty=qty)
        self.assertEqual(production_id.state, 'done')

    def create_wizard(self, mrp_production, qty=1):
        # Setting Environment
        wz_env = self.wizard.with_context(
            {'active_id': mrp_production.id,
             'active_ids': [mrp_production.id]})

        # Creating wizard to product
        wz_values = wz_env.default_get([])
        wz_brw = wz_env.create(wz_values)

        # Changing the quantity suggested
        wz_brw.product_qty = qty

        values = wz_brw.on_change_qty(wz_brw.product_qty, [])
        values = values.get('value')
        wz_brw.write(values)
        wz_brw.do_produce()
        return True

    def get_account_values(self, account_name):
        rec_ids = self.mrp_production_e.account_move_id.line_id.filtered(
            lambda l: l.account_id.name == account_name)
        res = []
        for rec_id in rec_ids:
            res.append((rec_id.debit, rec_id.credit))
        return res

    def test_01_check_workcenters_segments(self):
        self.produce_product(self.mrp_production_d, [1, 2])
        segments_costs = self.mrp_production_d.\
            get_workcenter_segmentation_amount()
        self.assertEqual(segments_costs['material_cost'], 0)
        self.assertEqual(segments_costs['landed_cost'], 0)
        self.assertEqual(segments_costs['production_cost'], 45)
        self.assertEqual(segments_costs['subcontracting_cost'], 0)

        self.produce_product(self.mrp_production_e, [1])

        production_vals = self.get_account_values('PRODUCTION_COST_ACCOUNT')
        self.assertEqual(production_vals, [(0, 7.5), (0, 7.5), (0, 15)],
                         'There is missing journal entries for production')

        deviation_vals = self.get_account_values(
            'INVENTORY_DEVIATION_ACCOUNT')
        self.assertEqual(deviation_vals, [(20, 0)],
                         'There is missing journal entries for deviation')

        wip_vals = self.get_account_values('WORK_IN_PROCESS')
        self.assertEqual(wip_vals, [(0, 20), (7.5, 0), (7.5, 0), (15, 0)],
                         'There is missing journal entries for production')

        segments_costs = self.mrp_production_e.\
            get_workcenter_segmentation_amount()
        self.assertEqual(segments_costs['material_cost'], 0)
        self.assertEqual(segments_costs['landed_cost'], 0)
        self.assertEqual(segments_costs['production_cost'], 15)
        self.assertEqual(segments_costs['subcontracting_cost'], 15)
