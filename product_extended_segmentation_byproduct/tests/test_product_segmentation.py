# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestProductSegmentation(TransactionCase):

    def setUp(self):
        super(TestProductSegmentation, self).setUp()
        self.prod_z_id = self.env.ref(
            'product_extended_segmentation_byproduct.product_z')
        self.prod_y_id = self.env.ref(
            'product_extended_segmentation_byproduct.product_y')
        self.env.ref('base.main_company').\
            write({'std_price_neg_threshold': 100})
        self.wizard = self.env['wizard.price']

        # use mrp_workcenter_segmentation routing defined for E production
        self.env.ref('product_extended_segmentation_byproduct.bom_product_z').\
            write({'routing_id': self.ref('mrp_workcenter_segmentation.'
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

    def test_01_product_update_with_subproducts(self):
        current_price = self.prod_z_id.standard_price
        self.assertEqual(current_price, 80, "It must be price=80 at first")
        self.create_update_wizard(self.prod_z_id.product_tmpl_id,
                                  False, True)
        self.assertEqual(self.prod_z_id.standard_price, 85)
        # 30(C) + 50(D) - 10(X * 2) - 15(Y)
        self.assertEqual(self.prod_z_id.material_cost, 55)
        self.assertEqual(self.prod_z_id.landed_cost, 0)
        # 15(E)
        self.assertEqual(self.prod_z_id.production_cost, 15)
        # 15(E)
        self.assertEqual(self.prod_z_id.subcontracting_cost, 15)

    def test_02_product_update_with_subproducts_with_segments(self):
        current_price_z = self.prod_z_id.standard_price
        self.assertEqual(current_price_z, 80, "It must be price=80 at first")
        current_price_y = self.prod_y_id.standard_price
        self.assertEqual(current_price_y, 15, "It must be price=15 at first")
        self.create_update_wizard(self.prod_y_id.product_tmpl_id,
                                  True, True)
        self.create_update_wizard(self.prod_z_id.product_tmpl_id,
                                  True, True)

        self.assertEqual(self.prod_y_id.standard_price, 30)
        # B(20)
        self.assertEqual(self.prod_y_id.material_cost, 20)
        self.assertEqual(self.prod_y_id.landed_cost, 0)
        self.assertEqual(self.prod_y_id.production_cost, 10)
        # 15(E)
        self.assertEqual(self.prod_y_id.subcontracting_cost, 0)

        self.assertEqual(self.prod_z_id.standard_price, 55)
        # A(10) + B(20) + C(30) - 10(X*2=5*2) - 20(Y)
        self.assertEqual(self.prod_z_id.material_cost, 30)
        self.assertEqual(self.prod_z_id.landed_cost, 0)
        # 20 = 15(E) + 5(D) - 10(Y)
        self.assertEqual(self.prod_z_id.production_cost, 10)
        # 15(E)
        self.assertEqual(self.prod_z_id.subcontracting_cost, 15)
