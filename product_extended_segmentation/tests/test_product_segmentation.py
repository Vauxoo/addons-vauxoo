from odoo.tests.common import TransactionCase


class TestProductSegmentation(TransactionCase):

    def setUp(self):
        super(TestProductSegmentation, self).setUp()
        self.prod_e_id = self.env.ref(
            'product_extended_segmentation.producto_e')
        self.prod_d_id = self.env.ref(
            'product_extended_segmentation.producto_d')
        self.template_d_id = self.prod_d_id.product_tmpl_id
        self.template_e_id = self.prod_e_id.product_tmpl_id
        # use mrp_workcenter_segmentation routing defined for E production
        self.env.ref('product_extended_segmentation.bom_product_e').write({
            'routing_id': self.ref('mrp_workcenter_segmentation.'
                                   'routing_segmentation_e_product')
        })

    def test_01_product_update_with_production_sgmnts_recursive(self):
        self.prod_e_id.compute_segmetation_price()
        self.assertEqual(self.prod_e_id.standard_price, 92.5)
        # A(10) + B(20) + C(30)
        self.assertEqual(self.prod_e_id.material_cost, 60)
        self.assertEqual(self.prod_e_id.landed_cost, 0)
        # 20 = 15(E) + 5(D)
        self.assertEqual(self.prod_e_id.production_cost, 25)
        # 15(E)
        self.assertEqual(self.prod_e_id.subcontracting_cost, 7.5)

    def test_02_test_threshold_no_update(self):
        self.run_test_threshold_no_update()

    def test_03_test_threshold_th_30_update(self):
        self.company_id.write({'std_price_neg_threshold': 30})
        # ============================
        # ==== PRODUCT D
        # ============================
        self.assertEqual(self.template_d_id.standard_price, 50,
                         'Standard Price for D should be 50')
        self.prod_d_id.compute_segmetation_price()

        # check what recursive returns
        self.assertEqual(self.template_d_id.standard_price, 40,
                         'Recursive cost for D should be keep at 40')
        # check production_cost
        self.assertEqual(self.template_d_id.production_cost, 10,
                         'Production Cost for D should be 10')
        # check material_cost
        self.assertEqual(self.template_d_id.material_cost, 30,
                         'Production Cost for D should be 10')
        # ============================
        # ==== PRODUCT E
        # ============================
        self.assertEqual(self.prod_e_id.standard_price, 80,
                         'Standard Price for E should be 80')
        self.prod_e_id.compute_segmetation_price()

        # check what recursive returns
        self.assertEqual(self.prod_e_id.standard_price, 92.5,
                         'Recursive cost for E should be keep at 75')
        # check production_cost
        self.assertEqual(self.prod_e_id.production_cost, 25,
                         'Production Cost for E should be 25')

    def test_03_write_real_cost_product_price_using_wizard(self):
        self.run_test_write_real_cost_product_price_using_wizard()
