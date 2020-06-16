from odoo.tests import TransactionCase
from odoo.exceptions import ValidationError


class ProductSegmentationTransactionCase(TransactionCase):

    def setUp(self):
        super().setUp()
        self.company_id = self.env.user.company_id
        self.env.ref('base.main_company').write({'std_price_neg_threshold': 100})
        self.segmentation_cost = [
            'landed_cost',
            'subcontracting_cost',
            'material_cost',
            'production_cost',
        ]

    def run_test_threshold_no_update(self):
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

    def run_test_write_real_cost_product_price_using_wizard(self):
        self.prod_d_id.write({
            'property_cost_method': 'fifo',
            'standard_price': 20.0
        })
        self.prod_d_id.compute_segmetation_price()
        old_price = self.template_e_id.standard_price
        old_values = {}.fromkeys(self.segmentation_cost, .0)
        self.assertNotEqual(old_price, self.prod_d_id.standard_price)
        self.assertEqual(old_values['landed_cost'], self.template_e_id.landed_cost,
                         "landed_cost have been written wrongly")
        self.assertEqual(
            old_values['subcontracting_cost'],
            self.template_e_id.subcontracting_cost,
            "subcontracting_cost have been written wrongly")
        self.assertNotEqual(
            old_values['material_cost'],
            self.prod_d_id.material_cost,
            "material_cost have been written wrongly")
        self.assertNotEqual(
            old_values['production_cost'],
            self.prod_d_id.production_cost,
            "production_cost have been written wrongly")
