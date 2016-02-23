# -*- coding: utf-8 -*-

from stock_landed_costs_average.tests.test_stock_landed_common \
    import TestStockLandedCommon


class TestLandedCostRevert(TestStockLandedCommon):

    def setUp(self):
        super(TestLandedCostRevert, self).setUp()
        self.company_id = self.env.ref('base.main_company')
        self.slc_id = self.env.ref('stock_landed_costs_average.slc_02')

        self.product_freight_id = self.env.ref(
            'stock_landed_costs_average'
            '.service_standard_periodic_landed_cost_1')
        self.account_freight_id = self.env.ref(
            'stock_landed_costs_average.freight_account')
        self.product_id = self.env.ref(
            'stock_landed_costs_average.product_mouse')
        self.supplier_id = self.env.ref('base.res_partner_13')
        self.customer_id = self.env.ref('base.res_partner_23')
        self.transactions = [
            {
                'cost': 20, 'qty': 2,
                'avg': 20, 'is_po': True,
            },
            {
                'cost': 40, 'qty': 3,
                'avg': 32, 'is_po': True,
            },
            {
                'cost': 32, 'qty': 1,
                'avg': 32, 'is_po': False,
            },
            {
                'cost': 64, 'qty': 4,
                'avg': 48, 'is_po': True,
            },
            {
                'cost': 48, 'qty': 4,
                'avg': 48, 'is_po': False,
            },
        ]
        self.expected_values = {
            self.ref('account.stk'): {
                'credit': [40, 24],
                'debit': [40, 24],
            },
            self.ref('account.a_expense'): {
                'credit': [24],
                'debit': [24],
            },
            self.account_freight_id.id: {
                'credit': [40],
                'debit': [40],
            },
        }

    def create_and_validate_landed_costs(self, picking_id):
        slc_id = self.slc.create({
            'account_journal_id': self.ref(
                'stock_landed_costs_average.stock_landed_cost_1'),
            'picking_ids': [(4, picking_id.id), ],
            'cost_lines': [
                (0, 0, {
                    'name': 'freight',
                    'product_id': self.product_freight_id.id,
                    'account_id': self.account_freight_id.id,
                    'split_method': 'by_quantity',
                    'price_unit': 40,
                }),
            ]
        })
        self.assertEqual(len(slc_id.picking_ids), 1)
        self.assertEqual(len(slc_id.cost_lines), 1)
        slc_id.compute_landed_cost()
        self.assertEqual(len(slc_id.valuation_adjustment_lines), 1)
        slc_id.button_validate()

        return slc_id

    def test_01_landed_cost_revert(self):
        card_lines = {}
        for trx in self.transactions:
            # purchase
            if trx['is_po']:
                trx['id'] = self.create_purchase_order(trx)
            else:  # sale
                trx['id'] = self.create_sale_order(trx)
            trx['picking_ids'] = trx['id'].picking_ids

        card_lines['before_landed'] = self.get_stock_card_lines(
            self.product_id.id)
        picking_id = self.transactions[0]['picking_ids']

        landed_cost_id = self.create_and_validate_landed_costs(picking_id)
        self.validate_acct_entries_values(
            landed_cost_id, self.product_id,  self.expected_values)

        card_lines['after_landed'] = self.get_stock_card_lines(
            self.product_id.id)

        revert_landed_cost_id = self.revert_landed_cost(landed_cost_id)
        self.validate_acct_entries_values(
            revert_landed_cost_id, self.product_id, self.expected_values)

        card_lines['after_revert'] = self.get_stock_card_lines(
            self.product_id.id)

        # check for values before applying landed cost and after revert landed
        # cost are the same
        self.assertEqual(
            card_lines['before_landed'], card_lines['after_revert'],
            'Something is not right with before_landed={0} '
            'and after_revert={1}'.format(card_lines['before_landed'],
                                          card_lines['after_revert']))

    def validate_acct_entries_values(self, landed_cost_id, product_id, vals):
        acct_move_id = landed_cost_id.account_move_id
        self.assertEqual(acct_move_id.mapped('line_id.product_id'), product_id)
        for aml_id in acct_move_id.line_id:
            acct_id = aml_id.account_id.id
            debit = aml_id.debit
            credit = aml_id.credit

            # check values expected for credit and debit
            self.assertTrue(
                credit and credit in vals[acct_id]['credit'] or
                debit and debit in vals[acct_id]['debit'])
