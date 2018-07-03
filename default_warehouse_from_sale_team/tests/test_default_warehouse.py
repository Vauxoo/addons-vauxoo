# coding: utf-8

from openerp.tests.common import TransactionCase


class TestSalesTeamDefaultWarehouse(TransactionCase):

    def setUp(self):
        super(TestSalesTeamDefaultWarehouse, self).setUp()
        self.company = self.env.ref('base.main_company')
        self.partner = self.env.ref('base.res_partner_12')
        self.sale_obj_new = self.env['sale.order']
        self.purchase_obj = self.env['purchase.order']
        self.purchase_requisition_obj = self.env['purchase.requisition']
        self.res_user_obj = self.env['res.users']
        self.pick_type_obj = self.env['stock.picking.type']

        # user with team
        self.demo_user = self.env.ref('base.user_demo')
        self.test_wh = self.env.ref('stock.stock_warehouse_shop0')
        self.sales_team = self.env.ref('sales_team.crm_team_1')
        self.sales_team.write({'default_warehouse': self.test_wh.id})
        self.demo_user.write(
            {'sale_team_id': self.sales_team.id,
             'sale_team_ids': [(4, self.sales_team.id, None)]})

        # Products
        self.product = self.env.ref('product.product_product_11')
        self.product_uom = self.env.ref('product.product_uom_unit')

    def test_default_picking_type_purchase_requisition(self):
        """Validate the picking type by default from sale team warehouse in
        purchase requisition"""

        values = self.purchase_requisition_obj.sudo(
            self.demo_user).default_get([])
        pick_type_id = self.pick_type_obj.browse(
            values.get('picking_type_id'))

        purchase_id = self.purchase_requisition_obj.sudo(
            self.demo_user).create({})

        self.assertEqual(purchase_id.picking_type_id, pick_type_id,
                         'Default picking type is not the'
                         'set on the sales team related to de user.')

    def test_default_picking_type_purchase(self):
        """Validate picking type by default from sale team warehouse in
        purchase order"""
        purchase_values = {
            'partner_id': self.partner.id,
            'name': 'Purchase with sale team'
        }

        values = self.purchase_obj.sudo(self.demo_user).default_get([])
        pick_type_id = self.pick_type_obj.browse(
            values.get('picking_type_id'))

        purchase_id = self.purchase_obj.sudo(self.demo_user).create(
            purchase_values)

        self.assertEqual(purchase_id.picking_type_id, pick_type_id,
                         'Default picking type is not the'
                         'set on the sales team related to de user.')

    def test_proper_behavior(self):
        """1.- Testing that the Demo User has not sales team set.
        2.-Testing that the sales order created by Demo User has
        the main warehouse assigned by default.
        3.- Writing a sales team to Demo user and a default warehouse for
        the sales team related to the Demo User.
        4.- Testing that the sales order created by Demo User after
        the sales team assignation has the default warehouse set
        on the user sales team.
        """
        main_wh = self.env.ref('stock.warehouse0')
        # user without team
        user_without_team = self.demo_user.copy({'sale_team_id': False})
        sale_brw1 = self.sale_obj_new.sudo(user_without_team).create({
            'name': 'Tests Main Sale Order',
            'company_id': self.company.id,
            'partner_id': self.partner.id,
        })
        sale_brw2 = self.sale_obj_new.sudo(self.demo_user).create({
            'name': 'Tests Sales Team Sale Order',
            'company_id': self.company.id,
            'partner_id': self.partner.id,
        })
        self.assertEqual(sale_brw1.warehouse_id.id, main_wh.id,
                         'Default warehouse is not the main warehouse.')
        self.assertEqual(sale_brw2.warehouse_id.id, self.test_wh.id,
                         'Default warehouse is not the warehouse'
                         'set on the sales team related to de user.')

    def test_warehouse_team_sale_policy(self):
        """Verify that the policy is created with the daily defined in the
        sales team for that warehouse
        """
        account_id = self.env['account.account'].search([], limit=1)
        test_wh = self.env.ref(
            'default_warehouse_from_sale_team.stock_warehouse_default_team'
        )
        sales_team = self.env.ref(
            'default_warehouse_from_sale_team.section_sales_default_team'
        )
        payment_term = self.env.ref('account.account_payment_term_immediate')
        self.product.categ_id.write({
            'property_valuation': 'real_time',
            'property_stock_account_input_categ_id': account_id.id,
            'property_stock_account_output_categ_id': account_id.id,
            })

        sale = self.sale_obj_new.sudo(self.demo_user).create({
            'name': 'Tests Main Sale Order',
            'company_id': self.company.id,
            'partner_id': self.partner.id,
            'warehouse_id': test_wh.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': 1.0,
                'price_unit': 100.0,
                'product_uom': self.product_uom.id,
            })],
            'payment_term_id': payment_term.id,
            'team_id': sales_team.id,
        })

        # Confirm sale order
        sale.sudo().action_confirm()
        pick = sale.picking_ids
        pick.force_assign()
        pick.move_lines.write({'quantity_done': 1})
        pick.button_validate()

        self.assertEqual(
            sale.team_id.journal_stock_id.id,
            pick.move_lines.account_move_ids.journal_id.id,
            'Daily defined in Default sales team is not policy sale order.')
