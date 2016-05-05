# coding: utf-8
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
###############################################################################
#    Credits:
#    Coded by: Yanina Aular <yani@vauxoo.com>
#    Planified by: Gabriela Quilarque <gabriela@vauxoo.com>
#    Audited by: Nhomar Hernandez <nhomar@vauxoo.com>
###############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################


from openerp.tests.common import TransactionCase


class TestLotNotRepeated(TransactionCase):
    """Test that the lot is not repeated when item was splited
    """

    def setUp(self):
        super(TestLotNotRepeated, self).setUp()
        self.stock_transfer_details = self.env["stock.transfer_details"]
        self.stock_transfer_details_items = \
            self.env["stock.transfer_details_items"]
        self.stock_picking = self.env["stock.picking"]
        self.stock_production_lot = self.env["stock.production.lot"]

    def test_01(self):

        lot = self.env.ref("stock_transfer_avoid_lot"
                           "_repeated_split."
                           "test_lot_not_repeated_1")

        transfer_rec = self.stock_transfer_details.create({
            "picking_source_location_id":
            self.env.ref("stock.stock_location_suppliers").id,
            "picking_destination_location_id":
            self.env.ref("stock.stock_location_company").id,
        })

        item_1 = self.stock_transfer_details_items.create({
            "transfer_id": transfer_rec.id,
            "product_id": self.env.ref("product.product_product_8").id,
            "product_uom_id": self.env.ref("product.product_uom_unit").id,
            "quantity": 10,
            "sourceloc_id":
            self.env.ref("stock.stock_location_suppliers").id,
            "destinationloc_id":
            self.env.ref("stock.stock_location_company").id,
            "lot_id": lot.id,
        })

        item_1.split_quantities()
        item_1.split_quantities()

        self.assertEquals(item_1.quantity,
                          8.0)

        for item in transfer_rec.item_ids:
            if item.quantity == 1:
                self.assertEquals(item.lot_id.id,
                                  False)
            else:
                self.assertEquals(item.lot_id,
                                  lot)
