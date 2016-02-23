# -*- coding: utf-8 -*-

from stock_landed_costs_average.tests.test_stock_landed_common \
    import TestStockLandedCommon


class TestLandedCostAverage(TestStockLandedCommon):

    def setUp(self):
        super(TestLandedCostAverage, self).setUp()
        self.company_id = self.env.ref('base.main_company')
        self.slc_id = self.env.ref('stock_landed_costs_average.slc_02')
        self.customer_location = self.env.ref('stock.stock_location_customers')
        self.supplier_location = self.env.ref('stock.stock_location_suppliers')
        self.supplier_id = self.env.ref('base.res_partner_13')
        self.customer_id = self.env.ref('base.res_partner_23')
        self.product_id = self.env.ref(
            'stock_landed_costs_average.product_mouse')
        self.transactions = [
            {  # 1 buy 8 items
                'name': 'slca_po_01',
                'is_po': True, 'is_return': False, 'cost': 10, 'qty': 8,
                'avg': 10, 'move_val': 80, 'inv_val': 80,
            },
            {  # 2 buy 4 items
                'name': 'slca_po_02',
                'is_po': True, 'is_return': False, 'cost': 16, 'qty': 4,
                'avg': 20, 'move_val': 40, 'inv_val': 40,
            },
            {  # 3 sale 10 items
                'name': 'slca_so_01',
                'is_po': False, 'is_return': False, 'cost': 12, 'qty': 10,
                'avg': 12, 'move_val': 120, 'inv_val': 24,
            },
            {  # 4 sale 1 item
                'name': 'slca_so_02',
                'is_po': False, 'is_return': False, 'cost': 12, 'qty': 1,
                'avg': 12, 'move_val': 12, 'inv_val': 12,
                'origin_name': 'po_01',
            },
            {  # 5 vendor return 1 item
                'name': 'slca_ret_po_01',
                'is_po': True, 'is_return': True, 'cost': 12, 'qty': 1,
                'avg': 12, 'move_val': 12, 'inv_val': 0,
                'origin_name': 'slca_po_01', 'partner_id': self.supplier_id,
            },
        ]

    def get_origin_picking(self, origin_name):
        for trx in self.transactions:
            if trx['name'] == origin_name:
                return trx['id'].picking_ids
        return False

    def test_01_do_transactions(self):
        for trx in self.transactions:
            # purchase
            if trx['is_po'] and not trx['is_return']:
                trx['id'] = self.create_purchase_order(trx)

            # vendor return
            if trx['is_po'] and trx['is_return']:
                trx['origin_id'] = self.get_origin_picking(trx['origin_name'])
                trx['id'] = self.create_return(trx)

            # sale
            if not trx['is_po'] and not trx['is_return']:
                trx['id'] = self.create_sale_order(trx)
        card_lines = self.env['stock.card.product'].\
            _stock_card_move_get(self.product_id.id)['res']
        last_item = card_lines[-1]
        self.assertEqual(last_item['product_qty'], 0)
        self.assertEqual(last_item['inventory_valuation'], 0)
