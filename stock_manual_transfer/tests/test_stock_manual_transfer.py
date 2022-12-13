from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import Form, TransactionCase, tagged


@tagged("-at_install", "post_install")
class TestStock(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.ref("base.main_company")
        cls.product = cls.env.ref("product.product_product_6")
        cls.warehouse = cls.env.ref("stock_manual_transfer.demo_warehouse_01")
        cls.sequence_manual_transfer = cls.env.ref("stock_manual_transfer.sequence_transfer")
        cls.warehouse_route_reception = cls.env.ref("stock_manual_transfer.demo_wh_route_reception")
        cls.today = fields.Date.context_today(cls.company)
        cls.location_suppliers = cls.env.ref("stock.stock_location_suppliers")
        cls.manual_transfer_group = cls.env.ref("stock_manual_transfer.group_stock_manual_transfer")

    def create_manual_transfer(self):
        transfer = Form(self.env["stock.manual_transfer"])
        transfer.route_id = self.warehouse_route_reception
        transfer.warehouse_id = self.warehouse
        transfer = transfer.save()
        self.create_manual_transfer_line(transfer)
        return transfer

    def create_manual_transfer_line(self, transfer):
        with Form(transfer) as tr, tr.transfer_line_ids.new() as line:
            line.product_id = self.product
            line.product_uom_qty = 1

    def test_01_manual_transfer(self):
        """Test creating a manual transfer and validating it so pickings are created"""
        # Create transfer and check default values
        transfer = self.create_manual_transfer()
        expected_name = "MT/%s/%05d" % (self.today.year, self.sequence_manual_transfer.number_next_actual - 1)
        self.assertRecordValues(
            records=transfer,
            expected_values=[
                {
                    "name": expected_name,
                    "state": "draft",
                    "warehouse_id": self.warehouse.id,
                    "picking_ids": [],
                    "procurement_group_id": False,
                }
            ],
        )

        # Validate and check pickings were created
        transfer.action_validate()
        self.assertEqual(transfer.state, "valid")
        self.assertEqual(transfer.procurement_group_id.name, expected_name)
        pickings = transfer.picking_ids
        self.assertRecordValues(
            records=pickings.move_line_ids,
            expected_values=[
                {
                    "product_id": self.product.id,
                    "product_uom_qty": 1.0,
                    "location_id": self.location_suppliers.id,
                    "location_dest_id": self.warehouse.lot_stock_id.id,
                    "origin": expected_name,
                    "state": "assigned",
                },
            ],
        )

        # Use action to open pickings
        action_res = transfer.action_view_pickings()
        opened_pickings = self.env[action_res["res_model"]].search(action_res["domain"])
        self.assertEqual(pickings, opened_pickings)

        # Once a transfer is validated, we shouldn't be able to delete it
        error_msg = "You can not delete a validated transfer"
        with self.assertRaisesRegex(ValidationError, error_msg):
            transfer.unlink()

        # But if it's one in draft, we should be able to delete it, even if it has lines
        draft_transfer = self.create_manual_transfer()
        draft_transfer.unlink()

    def test_02_no_warehouse_in_route(self):
        error_msg = "The selected route doesn't have configured rules on the selected warehouse."
        self.warehouse_route_reception.rule_ids.warehouse_id = False
        transfer = self.create_manual_transfer()
        with self.assertRaisesRegex(ValidationError, error_msg):
            transfer.action_validate()
