from odoo.addons.product_extended_segmentation.tests.common import ProductSegmentationTransactionCase


class TestProductSegmentation(ProductSegmentationTransactionCase):

    def setUp(self):
        super(TestProductSegmentation, self).setUp()
        self.prod_e_id = self.env.ref(
            'product_extended_segmentation_byproduct.producto_e')
        self.prod_d_id = self.env.ref(
            'product_extended_segmentation_byproduct.producto_d')
        self.template_d_id = self.prod_d_id.product_tmpl_id
        self.template_e_id = self.prod_e_id.product_tmpl_id
        self.env.ref('base.main_company').\
            write({'std_price_neg_threshold': 100})
        # use mrp_workcenter_segmentation routing defined for E production
        self.env.ref('product_extended_segmentation_byproduct.bom_product_e').write({
            'routing_id': self.ref('mrp_workcenter_segmentation.routing_segmentation_e_product')
        })

    def test_01_product_update_with_production_sgmnts_with_byproducts(self):
        self.prod_e_id.compute_segmetation_price()
        self.assertEqual(self.prod_e_id.standard_price, 65)
        # A(10) + B(20) + C(30) - F*3(2.5*3=7.5) - G(20)
        self.assertEqual(self.prod_e_id.material_cost, 32.5)
        self.assertEqual(self.prod_e_id.landed_cost, 0)
        # 20 = 15(E) + 5(D)
        self.assertEqual(self.prod_e_id.production_cost, 25)
        # 15(E)
        self.assertEqual(self.prod_e_id.subcontracting_cost, 7.5)

    def test_02_test_threshold_no_update(self):
        self.run_test_threshold_no_update()

    def test_03_test_threshold_th_40_update(self):
        self.company_id.write({'std_price_neg_threshold': 40})
        # ============================
        # ==== PRODUCT D
        # ============================
        self.assertEqual(self.template_d_id.standard_price, 50,
                         'Standard Price for D should be 50')
        self.prod_d_id.compute_segmetation_price()

        # check what recursive returns
        self.assertEqual(self.template_d_id.standard_price, 32.5,
                         'Recursive cost for D should be keep at 32.5')
        # check production_cost
        self.assertEqual(self.template_d_id.production_cost, 10,
                         'Production Cost for D should be 10')
        # check material_cost
        self.assertEqual(self.template_d_id.material_cost, 22.5,
                         'Material Cost for D should be 22.5')
        # ============================
        # ==== PRODUCT E
        # ============================
        self.assertEqual(self.prod_e_id.standard_price, 80,
                         'Standard Price for E should be 80')
        self.prod_e_id.compute_segmetation_price()

        # check what recursive returns
        self.assertEqual(self.prod_e_id.standard_price, 65,
                         'Recursive cost for E should be keep at 65')
        # check production_cost
        self.assertEqual(self.prod_e_id.production_cost, 25,
                         'Production Cost for E should be 25')
        self.assertEqual(self.prod_e_id.material_cost, 32.5,
                         'Material Cost for E should be 32.5')
        self.assertEqual(self.prod_e_id.subcontracting_cost, 7.5,
                         'Subcontracting Cost for E should be 7.5')

    def test_03_write_real_cost_product_price_using_wizard(self):
        self.run_test_write_real_cost_product_price_using_wizard()
