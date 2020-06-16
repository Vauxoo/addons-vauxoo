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
