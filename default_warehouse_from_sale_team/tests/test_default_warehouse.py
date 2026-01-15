from odoo import Command
from odoo.tests import Form, TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestSalesTeamDefaultWarehouse(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.ref("base.main_company")
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.purchase_obj = cls.env["purchase.order"]
        cls.purchase_requisition_obj = cls.env["purchase.requisition"]
        cls.pick_type_obj = cls.env["stock.picking.type"]

        # Create test warehouse
        cls.test_wh = cls.env["stock.warehouse"].create({
            "name": "Team Default Warehouse",
            "code": "TDW",
            "company_id": cls.company.id,
        })

        # Create sales team with default warehouse
        cls.sales_team = cls.env["crm.team"].create({
            "name": "Test Sales Team",
            "default_warehouse_id": cls.test_wh.id,
        })

        # Create demo user with required groups
        cls.demo_user = cls.env["res.users"].create({
            "name": "Demo User",
            "login": "demo_user_test",
            "email": "demo@test.com",
            "company_id": cls.company.id,
            "company_ids": [Command.link(cls.company.id)],
            "sale_team_id": cls.sales_team.id,
            "sale_team_ids": [Command.link(cls.sales_team.id)],
            "group_ids": [
                Command.link(cls.env.ref("sales_team.group_sale_salesman").id),
                Command.link(cls.env.ref("purchase.group_purchase_user").id),
            ],
        })

        # Create team membership - this triggers sale_team_id compute
        cls.env["crm.team.member"].create({
            "user_id": cls.demo_user.id,
            "crm_team_id": cls.sales_team.id,
        })

        # Create test product
        cls.product_uom = cls.env.ref("uom.product_uom_unit")
        cls.product = cls.env["product.product"].create({
            "name": "Test Product",
            "type": "consu",
            "uom_id": cls.product_uom.id,
        })

        # User without team should get main warehouse
        cls.user_without_team = cls.env["res.users"].create({
            "name": "User No Team",
            "login": "user_no_team_test",
            "email": "noteam@test.com",
            "company_id": cls.company.id,
            "company_ids": [Command.link(cls.company.id)],
            "sale_team_id": False,
            "group_ids": [
                Command.link(cls.env.ref("sales_team.group_sale_salesman").id),
            ],
        })

    def create_sale_order(self, partner=None, user=None, **line_kwargs):
        if partner is None:
            partner = self.partner
        if user is None:
            user = self.env.user
        # Create order with explicit user_id to ensure correct warehouse computation
        sale_order = self.env["sale.order"].with_user(user).create({
            "partner_id": partner.id,
            "user_id": user.id,  # Explicit to trigger warehouse compute correctly
        })
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
        values = self.purchase_requisition_obj.with_user(self.demo_user).default_get([])
        pick_type_id = self.pick_type_obj.browse(values.get("picking_type_id"))

        purchase_id = self.purchase_requisition_obj.with_user(self.demo_user).create({})

        self.assertEqual(
            purchase_id.picking_type_id,
            pick_type_id,
            "Default picking type is not the set on the sales team related to de user.",
        )

    def test_02_default_picking_type_purchase(self):
        """Validate picking type by default from sale team warehouse in
        purchase order"""
        purchase_values = {"partner_id": self.partner.id, "name": "Purchase with sale team"}

        values = self.purchase_obj.with_user(self.demo_user).default_get([])
        pick_type_id = self.pick_type_obj.browse(values.get("picking_type_id"))

        purchase_id = self.purchase_obj.with_user(self.demo_user).create(purchase_values)

        self.assertEqual(
            purchase_id.picking_type_id,
            pick_type_id,
            "Default picking type is not the set on the sales team related to de user.",
        )

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
        main_wh = self.env.ref("stock.warehouse0")

        # Verify setup is correct
        self.assertEqual(self.demo_user.sale_team_id, self.sales_team)
        self.assertEqual(self.sales_team.default_warehouse_id, self.test_wh)
        sale_order1 = self.create_sale_order(user=self.user_without_team)
        sale_order2 = self.create_sale_order(user=self.demo_user)

        self.assertEqual(
            sale_order1.warehouse_id, main_wh,
            "User without team should get main warehouse."
        )
        self.assertEqual(
            sale_order2.warehouse_id, self.test_wh,
            f"User with team should get team warehouse. "
            f"User sale_team_id: {self.demo_user.sale_team_id.name}, "
            f"Team warehouse: {self.sales_team.default_warehouse_id.name}"
        )

    def test_04_warehouse_team_sale_policy(self):
        """Verify that the policy is created with the daily defined in the
        sales team for that warehouse
        """
        account_id = self.env["account.account"].search([], limit=1)
        self.product.categ_id.write(
            {
                "property_valuation": "real_time",
                "property_stock_account_input_categ_id": account_id.id,
                "property_stock_account_output_categ_id": account_id.id,
            }
        )
        sale = self.create_sale_order(user=self.demo_user)

        # Confirm sale order
        sale.sudo().action_confirm()
        pick = sale.picking_ids
        pick.action_assign()
        pick.move_ids.write({"quantity": 1, "picked": True})
        pick.button_validate()
