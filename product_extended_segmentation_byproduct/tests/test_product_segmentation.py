# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
SEGMENTATION_COST = [
    'landed_cost',
    'subcontracting_cost',
    'material_cost',
    'production_cost',
]


class TestProductSegmentation(TransactionCase):

    def setUp(self):
        super(TestProductSegmentation, self).setUp()
        self.company_id = self.env.user.company_id
        self.prod_e_id = self.env.ref(
            'product_extended_segmentation_byproduct.producto_e')
        self.prod_d_id = self.env.ref(
            'product_extended_segmentation_byproduct.producto_d')
        self.template_d_id = self.prod_d_id.product_tmpl_id
        self.template_e_id = self.prod_e_id.product_tmpl_id
        self.env.ref('base.main_company').\
            write({'std_price_neg_threshold': 100})
        # use mrp_workcenter_segmentation routing defined for E production
        self.env.ref('product_extended_segmentation_byproduct.bom_product_e').\
            write({'routing_id': self.ref('mrp_workcenter_segmentation.'
                                          'routing_segmentation_e_product')
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
        msg_error = 'Bottom cost threshold must be positive'
        with self.assertRaisesRegexp(ValidationError, msg_error):
            self.company_id.write({'std_price_neg_threshold': -1})

        self.company_id.write({'std_price_neg_threshold': 0})
        # ============================
        # ==== PRODUCT D
        # ============================
        self.assertEqual(self.template_d_id.standard_price, 50,
                         'Standard Price for D should be 50')
        self.prod_d_id.compute_segmetation_price()

        # check what recursive returns
        self.assertEqual(self.template_d_id.standard_price, 50,
                         'Recursive cost for D should be keep at 50')
        # check production_cost
        self.assertEqual(self.template_d_id.production_cost, 0,
                         'Production Cost for D should be 0')

        # ============================
        # ==== PRODUCT E
        # ============================
        self.prod_e_id.standard_price = 300
        self.assertEqual(self.prod_e_id.standard_price, 300,
                         'Standard Price for %s should be %s' % (
                             self.prod_e_id.name, 80))
        self.prod_e_id.compute_segmetation_price()

        # check what recursive returns
        self.assertEqual(self.prod_e_id.standard_price, 300,
                         'Recursive cost for E should be keep at 80')

        # check production_cost
        self.assertEqual(self.prod_e_id.production_cost, 0,
                         'Production Cost for E should be 15')

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
        template_id = self.prod_e_id.product_tmpl_id
        self.prod_d_id.write({
            'property_cost_method': 'fifo',
            'standard_price': 20.0
        })
        self.prod_d_id.compute_segmetation_price()
        old_price = template_id.standard_price
        old_values = {}.fromkeys(SEGMENTATION_COST, .0)
        self.assertNotEqual(old_price, self.prod_d_id.standard_price)
        self.assertEqual(old_values['landed_cost'], template_id.landed_cost,
                         "landed_cost have been written wrongly")
        self.assertEqual(old_values['subcontracting_cost'],
                         template_id.subcontracting_cost,
                         "subcontracting_cost have been written wrongly")
        self.assertNotEqual(old_values['material_cost'],
                            self.prod_d_id.material_cost,
                            "material_cost have been written wrongly")
        self.assertNotEqual(old_values['production_cost'],
                            self.prod_d_id.production_cost,
                            "production_cost have been written wrongly")
