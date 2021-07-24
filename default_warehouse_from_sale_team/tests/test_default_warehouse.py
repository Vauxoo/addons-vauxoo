from odoo.tests import Form, TransactionCase


class TestSalesTeamDefaultWarehouse(TransactionCase):

    def setUp(self):
        super().setUp()
        self.company = self.env.ref('base.main_company')
        self.partner = self.env.ref('base.res_partner_12')
        self.purchase_obj = self.env['purchase.order']
        self.purchase_requisition_obj = self.env['purchase.requisition']
        self.res_user_obj = self.env['res.users']
        self.pick_type_obj = self.env['stock.picking.type']

        # user with team
        self.demo_user = self.env.ref('base.user_demo')
        self.test_wh = self.env.ref('default_warehouse_from_sale_team.stock_warehouse_default_team')
        self.sales_team = self.env.ref('sales_team.crm_team_1')
        self.sales_team.write({'default_warehouse_id': self.test_wh.id})
        self.demo_user.write({
            'sale_team_id': self.sales_team.id,
            'sale_team_ids': [(4, self.sales_team.id, None)],
            'company_id': self.company.id,
        })

        # Products
        self.product = self.env.ref('product.product_product_11')
        self.product_uom = self.env.ref('uom.product_uom_unit')

    def create_sale_order(self, partner=None, **line_kwargs):
        if partner is None:
            partner = self.partner
        sale_order = Form(self.env["sale.order"])
        sale_order.partner_id = partner
        sale_order = sale_order.save()
        self.create_so_line(sale_order, **line_kwargs)
        return sale_order

    def create_so_line(self, sale_order, product=None, quantity=1, price=100):
        if product is None:
            product = self.product
        with Form(sale_order) as so:
            with so.order_line.new() as line:
                line.product_id = product
                line.product_uom_qty = quantity
                line.price_unit = price

    def test_01_default_picking_type_purchase_requisition(self):
        """Validate the picking type by default from sale team warehouse in
        purchase requisition
        """
        values = self.purchase_requisition_obj.with_user(
            self.demo_user).default_get([])
        pick_type_id = self.pick_type_obj.browse(
            values.get('picking_type_id'))

        purchase_id = self.purchase_requisition_obj.with_user(
            self.demo_user).create({})

        self.assertEqual(purchase_id.picking_type_id, pick_type_id,
                         'Default picking type is not the'
                         'set on the sales team related to de user.')

    def test_02_default_picking_type_purchase(self):
        """Validate picking type by default from sale team warehouse in
        purchase order"""
        purchase_values = {
            'partner_id': self.partner.id,
            'name': 'Purchase with sale team'
        }

        values = self.purchase_obj.with_user(self.demo_user).default_get([])
        pick_type_id = self.pick_type_obj.browse(
            values.get('picking_type_id'))

        purchase_id = self.purchase_obj.with_user(self.demo_user).create(purchase_values)

        self.assertEqual(purchase_id.picking_type_id, pick_type_id,
                         'Default picking type is not the'
                         'set on the sales team related to de user.')

    def test_03_proper_behavior(self):
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
        self.uid = user_without_team
        sale_order1 = self.create_sale_order()
        self.uid = self.demo_user
        sale_order2 = self.create_sale_order()
        self.assertEqual(sale_order1.warehouse_id, main_wh, 'Default warehouse is not the main warehouse.')
        self.assertEqual(
            sale_order2.warehouse_id, self.test_wh,
            'Default warehouse is not the warehouse set on the sales team related to de user.')

    def test_04_warehouse_team_sale_policy(self):
        """Verify that the policy is created with the daily defined in the
        sales team for that warehouse
        """
        account_id = self.env['account.account'].search([], limit=1)
        sales_team = self.env.ref(
            'default_warehouse_from_sale_team.section_sales_default_team'
        )
        payment_term = self.env.ref('account.account_payment_term_immediate')
        self.product.categ_id.write({
            'property_valuation': 'real_time',
            'property_stock_account_input_categ_id': account_id.id,
            'property_stock_account_output_categ_id': account_id.id,
            })
        sale = self.create_sale_order()

        # Confirm sale order
        sale.sudo().action_confirm()
        pick = sale.picking_ids
        pick.action_assign()
        pick.move_lines.write({'quantity_done': 1})
        pick.button_validate()
