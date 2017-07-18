# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase


class TestSaleOrder(TransactionCase):
    """Test cases for sale.order model"""

    def setUp(self):
        super(TestSaleOrder, self).setUp()
        self.country_mx = self.env.ref('base.mx')
        self.state_mx_df = self.env.ref('base.state_mx_df')
        self.state_mx_col = self.env.ref('base.state_mx_col')
        self.partner_camp = self.env.ref('base.res_partner_12')
        self.supplier = self.env.ref('base.res_partner_3')
        self.ipad_mini = self.env.ref('product.product_product_6')

    def create_sale(self, line=None):
        line = line or {}
        line_values = {
            'product_id': self.ipad_mini.id,
            'product_uom': self.ipad_mini.uom_id.id,
            'product_uom_qty': 1,
            'price_unit': 32.0,
            'purchase_price': 10.0,
            'purchase_qty': 1,
            'supplier_id': self.supplier.id,
        }
        line_values.update(line)
        return self.env['sale.order'].create({
            'partner_id': self.partner_camp.id,
            'order_line': [(0, 0, line_values)],
        })

    def test_00_onchange_partner_id_dtype(self):
        """ This test validates that delivery method field only show deliveries
        available
        """
        max_value = 8620  # expected amount total = 10000
        over_10 = self.env.ref(
            'delivery_available_domain.delivery_over_10').id
        under_10 = self.env.ref(
            'delivery_available_domain.delivery_under_10').id
        inside_df = self.env.ref(
            'delivery_available_domain.delivery_inside_df').id
        outside_df = self.env.ref(
            'delivery_available_domain.delivery_outside_df').id
        # check deliveries available for orders over max_value
        order_line_vals = {'price_unit': max_value + 1}
        sale_1 = self.create_sale(order_line_vals)
        res = sale_1.onchange_partner_id_dtype()
        self.assertIn('domain', res)
        self.assertIn('carrier_id', res['domain'])
        self.assertIn(over_10, res['domain']['carrier_id'][0][2])
        self.assertNotIn(under_10, res['domain']['carrier_id'][0][2])

        # check deliveries available for partner inside metropolitan zone
        self.partner_camp.write({
            'country_id': self.country_mx.id,
            'state_id': self.state_mx_df.id,
        })
        res = sale_1.onchange_partner_id_dtype()
        self.assertIn('domain', res)
        self.assertIn('carrier_id', res['domain'])
        self.assertIn(inside_df, res['domain']['carrier_id'][0][2])
        self.assertNotIn(outside_df, res['domain']['carrier_id'][0][2])

        # check deliveries available for orders under max_value
        order_line_vals = {'price_unit': max_value - 1}
        sale_2 = self.create_sale(order_line_vals)
        res = sale_2.onchange_partner_id_dtype()
        self.assertIn('domain', res)
        self.assertIn('carrier_id', res['domain'])
        self.assertNotIn(over_10, res['domain']['carrier_id'][0][2])
        self.assertIn(under_10, res['domain']['carrier_id'][0][2])

        # check deliveries available for partner inside metropolitan zone
        self.partner_camp.write({
            'country_id': self.country_mx.id,
            'state_id': self.state_mx_col.id,
        })
        res = sale_2.onchange_partner_id_dtype()
        self.assertIn('domain', res)
        self.assertIn('carrier_id', res['domain'])
        self.assertNotIn(inside_df, res['domain']['carrier_id'][0][2])
        self.assertIn(outside_df, res['domain']['carrier_id'][0][2])
