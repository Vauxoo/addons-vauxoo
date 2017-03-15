# coding: utf-8

from __future__ import division
import logging
from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import Warning as UserError
_logger = logging.getLogger(__name__)

try:
    import pandas as pd
except ImportError:
    _logger.debug('Cannot `import pandas`.')


class StockCard(models.TransientModel):
    _name = 'stock.card'
    product_ids = fields.Many2many('product.product', string='Products')
    stock_card_product_ids = fields.One2many(
        'stock.card.product', 'stock_card_id', 'Product Stock Cards',
        help='Product Stock Cards')

    @api.multi
    def action_view_moves(self):
        """ Retrieve lines created by this Stock Card Wizard
        """
        self.ensure_one()
        ctx = self._context.copy()

        ir_model_obj = self.pool['ir.model.data']
        model, action_id = ir_model_obj.get_object_reference(
            self._cr, self._uid, 'stock_card',
            'stock_card_product_tree_action')
        action = self.pool[model].read(
            self._cr, self._uid, action_id, context=self._context)
        action['context'] = ctx
        # compute the number of invoices to display
        scm_ids = [scm_brw.id for scm_brw in self.stock_card_product_ids]
        # choose the view_mode accordingly
        if len(scm_ids) >= 1:
            action['domain'] = "[('id','in',[" + ','.join(
                [str(scm_id) for scm_id in scm_ids]
            ) + "])]"
        # else:
        #     raise UserError(
        #         _('Asked Product has not Moves to show'))
        return action

    @api.multi
    def generate_report(self):
        """ Retrieve Stock Card for products - Summary
        """
        self.ensure_one()
        ctx = self._context.copy()
        if not self.product_ids and ctx.get('active_ids'):
            self.write({'product_ids': [(4, ctx.get('active_ids'))]})
        if not self.product_ids:
            return

        return self.stock_card_inquiry_get()

    @api.multi
    def stock_card_inquiry_get(self):
        self.ensure_one()
        scp_obj = self.env['stock.card.product']
        self.stock_card_product_ids.unlink()
        # /!\ NOTE: Sudo to be invoke
        for product in self.product_ids:
            values = self.stock_card_inquiry_product(product)
            if not values:
                continue
            scp_obj.create(values)
        action = self.action_view_moves()
        return action

    @api.multi
    def stock_card_inquiry_product(self, product):
        scp_obj = self.env['stock.card.product']
        stock_valuation_account = \
            product.categ_id.property_stock_valuation_account_id
        stock_valuation_input = \
            product.categ_id.property_stock_account_input_categ or \
            product.property_stock_account_input
        stock_valuation_output = \
            product.categ_id.property_stock_account_output_categ or \
            product.property_stock_account_output
        stock_valuation_diff = \
            product.categ_id.\
            property_account_creditor_price_difference_categ or \
            product.property_account_creditor_price_difference
        if not (stock_valuation_account and stock_valuation_diff):
            return

        self._cr.execute("""
            SELECT  aml.account_id as account, sum(debit - credit)
            FROM account_move_line aml
                JOIN account_period ap
                ON aml.period_id = ap.id
            WHERE aml.account_id in %s
            AND aml.product_id = %s
            AND ap.special != True
            GROUP BY aml.account_id
            """, (
                (stock_valuation_account.id,
                    stock_valuation_input.id,
                    stock_valuation_output.id,
                    stock_valuation_diff.id), product.id))
        dat = self._cr.dictfetchall()
        values = {}
        for data in dat:
            if data['account'] == stock_valuation_account.id:
                product_valuation = (
                    product.qty_available * product.standard_price)
                product_acc_valuation = data and data['sum']
                diff_stock_val = product_valuation - product_acc_valuation
                percent = (
                    ((diff_stock_val) /
                        product_acc_valuation) * 100.0
                    if product_acc_valuation else 0.0)
                values.update({
                    'acc_valuation': product_acc_valuation,
                    'log_valuation': product_valuation,
                    'diff_stock_val': diff_stock_val,
                    'perc_diff_val': percent})
            if data['account'] == stock_valuation_input.id:
                values.update({'acc_input': data and data['sum']})
            if data['account'] == stock_valuation_output.id:
                values.update({'acc_output': data and data['sum']})
            if data['account'] == stock_valuation_diff.id:
                values.update({'acc_price_diff': data and data['sum']})

        values.update({'stock_card_id': self.id, 'product_id': product.id})
        scp_res = scp_obj._stock_card_move_get(product.id)
        cost = scp_obj.get_average(scp_res)['average']
        res = scp_res.get('res', [])
        date = res[-1]['date'] if res else None
        stock_card_qty = res[-1]['product_qty'] if res else 0.0
        diff = product.standard_price - cost
        values.update({
            'stock_card_cost': cost,
            'standard_price': product.standard_price,
            'diff_cost': diff,
            'date_stock_card': date,
            'logistical_qty': product.qty_available,
            'stock_card_qty': stock_card_qty,
            'diff_qty': product.qty_available - stock_card_qty,
            'diff_val': diff * product.qty_available,
        })
        return values


class StockCardProduct(models.TransientModel):
    _name = 'stock.card.product'
    _rec_name = 'product_id'
    product_id = fields.Many2one('product.product', string='Product',
                                 help='Gets the average price from the '
                                 'warehouse products')
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse',
                                   help='Gets the average price from the '
                                   'warehouse products')
    stock_card_move_ids = fields.One2many(
        'stock.card.move', 'stock_card_product_id', 'Product Moves',
        help='Product movements')
    stock_card_id = fields.Many2one(
        'stock.card', string='Stock Card',
        help='Gets the average price from the warehouse products')
    acc_input = fields.Float('Input Valuation')
    acc_output = fields.Float('Output Valuation')
    perc_diff_val = fields.Float('Val. Percentage Diff.')
    acc_price_diff = fields.Float('Account Price Difference Valuation')
    acc_valuation = fields.Float('Accounting Valuation')
    stock_card_cost = fields.Float('Stock Card Cost')
    standard_price = fields.Float('Logistical Cost')
    date_stock_card = fields.Datetime('Stock Card Date')
    diff_cost = fields.Float('Cost Difference')
    logistical_qty = fields.Float('Logistical Qty.')
    stock_card_qty = fields.Float('Stock Card Qty.')
    diff_qty = fields.Float('Qty Difference')
    diff_val = fields.Float('Valuation Difference')
    log_valuation = fields.Float('Logistical Valuation')
    diff_stock_val = fields.Float('Stock Valuation Diff.')
    adjustment_journal_entry = fields.Many2one(
        'account.move',
        'Adjustment Journal Entry')

    @api.multi
    def update_inquiry(self):
        sc_obj = self.env['stock.card']
        values = sc_obj.stock_card_inquiry_product(self.product_id)
        self.write(values)
        return True

    @api.multi
    def create_val_diff_journal_entry(self):
        self.ensure_one()
        if self.adjustment_journal_entry:
            # /|\ NOTE: Instead of skipping we could re-write the previous one
            return
        diff = -self.diff_stock_val
        if not diff:
            return
        move_obj = self.env['account.move']
        tmpl_obj = self.pool['product.template']

        ref = '[%(code)s] %(name)s' % dict(
            code=self.product_id.default_code, name=self.product_id.name)

        datas = tmpl_obj.get_product_accounts(
            self._cr,
            self._uid,
            self.product_id.product_tmpl_id.id,
        )

        move_vals = {
            'journal_id': datas['stock_journal'],
            'company_id':
            self.env['res.users'].browse(self._uid).company_id.id,
            'ref': ref,
        }

        base_vals = {
            'name': _('Stock Valuation Adjustment'),
            'ref': ref,
            'debit': 0,
            'credit': 0,
            'product_id': self.product_id.id,
        }

        diff_account = datas['property_difference_price_account_id']
        val_account = datas['property_stock_valuation_account_id']

        l1_vals = dict(
            base_vals,
            debit=diff if diff > 0 else 0,
            credit=-diff if diff < 0 else 0,
            account_id=diff_account,
        )
        l2_vals = dict(
            base_vals,
            debit=-diff if diff < 0 else 0,
            credit=diff if diff > 0 else 0,
            account_id=val_account,
        )
        move_vals.update({
            'line_id': [(0, 0, l1_vals), (0, 0, l2_vals)]})
        move_id = move_obj.create(move_vals)

        self.write({'adjustment_journal_entry': move_id.id})
        self.update_inquiry()
        return None

    def _get_fieldnames(self):
        return {
            'average': 'standard_price'
        }

    def map_field2write(self, field2write):
        res = {}
        field_names = self._get_fieldnames()
        for fn in field2write.keys():
            if fn not in field_names:
                continue
            res[field_names[fn]] = field2write[fn]
        return res

    def write_standard_price(self, product_id, field2write):
        # Write the standard price, as SUDO because a warehouse
        # manager may not have the right to write on products
        product_obj = self.env['product.product']
        field2write = self.map_field2write(field2write)
        product_obj.sudo().browse(product_id).write(field2write)

    @api.multi
    def get_locations(self, warehouse):
        """ Returns location ids of location that are contained in warehouse
        :param warehouse: browse record (stock.warehouse)
        """
        loc_obj = self.env["stock.location"]
        if not warehouse:
            return False
        locations = loc_obj.search(
            [('parent_left', '<=', warehouse.view_location_id.parent_right),
             ('parent_left', '>=', warehouse.view_location_id.parent_left)]).\
            filtered(lambda r: r.usage != 'view').mapped('id')
        return locations and tuple(locations) or False

    @api.multi
    def stock_card_move_get(self):
        self.ensure_one()
        if not (self.product_id.valuation == 'real_time' and
                self.product_id.cost_method in ('average', 'real')):
            return True
        self.stock_card_move_ids.unlink()
        location_ids = self.get_locations(self.warehouse_id)
        self.create_stock_card_lines(self.product_id.id, location_ids)
        return self.action_view_moves()

    def _get_quant_values(self, move_id, col='', inner='', where=''):
        query = ('''
                 SELECT
                     sqm_rel.quant_id AS quant_id,
                     COALESCE(cost, 0.0) AS cost,
                     COALESCE(qty, 0.0) AS qty,
                     propagated_from_id AS antiquant
                     %(col)s
                 FROM stock_quant_move_rel AS sqm_rel
                 INNER JOIN stock_quant AS sq ON sq.id = sqm_rel.quant_id
                 %(inner)s
                 WHERE sqm_rel.move_id = %(move_id)s
                 %(where)s
                 ''') % dict(move_id=move_id,
                             col=col, inner=inner, where=where)
        self._cr.execute(query)
        return self._cr.dictfetchall()

    def _get_price_on_consumed(self, row, vals, qntval):
        move_id = row['move_id']
        product_qty = vals['product_qty']
        delta_qty = vals['direction'] * row['product_qty']
        final_qty = product_qty + delta_qty
        vals['product_qty'] += (vals['direction'] * row['product_qty'])

        # TODO: move to `transit` could be a return
        # average is kept unchanged products are taken at average price
        if not vals['move_dict'].get(move_id):
            vals['move_dict'][move_id] = {}
        vals['move_dict'][move_id]['average'] = vals['average']

        antiquant = any([qnt['antiquant'] for qnt in qntval])
        if final_qty < 0 and antiquant:
            vals['move_dict'][move_id]['average'] = vals['average']
            vals['move_valuation'] = sum(
                [vals['average'] * qnt['qty'] for qnt in qntval
                 if qnt['qty'] > 0])
            return True

        vals['move_valuation'] = 0.0

        for qnt in qntval:
            if qnt['qty'] < 0:
                continue
            product_qty += vals['direction'] * qnt['qty']
            if product_qty >= 0:
                if not vals['rewind']:
                    vals['move_valuation'] += vals['average'] * qnt['qty']
                else:
                    vals['move_valuation'] += \
                        vals['prior_average'] * qnt['qty']
            else:
                if not vals['rewind']:
                    vals['move_valuation'] += vals['average'] * qnt['qty']
                else:
                    vals['move_valuation'] += \
                        vals['future_average'] * qnt['qty']

        # NOTE: For production
        # a) it could be a consumption: if so average is kept unchanged
        # products are taken at average price
        # TODO: Consider the case that
        # b) it could be a return: defective good, reworking, etc.
        return True

    def _get_price_on_supplier_return(self, row, vals, qntval):
        vals['product_qty'] += (vals['direction'] * row['product_qty'])
        # Cost is the one record in the stock_move, cost in the
        # quant record includes other segmentation cost: landed_cost,
        # material_cost, production_cost, subcontracting_cost
        # Inventory Value has to be decreased by the amount of purchase
        current_quants = set([qnt['quant_id'] for qnt in qntval])
        origin_quants = set()
        if row['origin_returned_move_id']:
            origin_quants = set(
                [qnt['quant_id']
                 for qnt in self._get_quant_values(
                     row['origin_returned_move_id'])])
        quants_exists = current_quants.issubset(origin_quants)
        # TODO: BEWARE price_unit needs to be normalised
        price = row['price_unit']
        # / ! \ This is missing when current move's quants are partially
        # located in origin's quants, so it's taking average cost temporarily
        if not quants_exists:
            price = vals['average']
        vals['move_valuation'] = sum([price * qnt['qty'] for qnt in qntval])
        return True

    def _get_price_on_supplied(self, row, vals, qntval):
        vals['product_qty'] += (vals['direction'] * row['product_qty'])
        # TODO: transit could be a return that shall be recorded at
        # average cost of transaction
        # average is to be computed considering all the segmentation
        # costs inside quant
        vals['move_valuation'] = sum(
            [qnt['cost'] * qnt['qty'] for qnt in qntval])
        return True

    def _get_price_on_customer_return(self, row, vals, qntval):
        vals['product_qty'] += (vals['direction'] * row['product_qty'])
        # NOTE: Identify the originating move_id of returning move
        origin_id = row['origin_returned_move_id'] or row['move_dest_id']
        # NOTE: Falling back to average in case customer return is
        # orphan, i.e., return was created from scratch
        old_average = (
            vals['move_dict'].get(origin_id) and
            vals['move_dict'][origin_id]['average'] or vals['average'])
        vals['move_valuation'] = sum(
            [old_average * qnt['qty'] for qnt in qntval])
        return True

    def _get_move_average(self, row, vals):
        qty = row['product_qty']
        vals['cost_unit'] = vals['move_valuation'] / qty if qty else 0.0

        vals['inventory_valuation'] += (
            vals['direction'] * vals['move_valuation'])
        # NOTE: there was Negative Quantity, therefore average and
        # valuation shall only consider new values
        if vals['previous_qty'] < 0 and vals['direction'] > 0:
            vals['accumulated_variation'] += vals['move_valuation']
            vals['accumulated_qty'] += row['product_qty']
            vals['average'] = (
                vals['accumulated_qty'] and
                vals['accumulated_variation'] / vals['accumulated_qty'] or
                vals['average'])

            if vals['product_qty'] >= 0:
                vals['accumulated_variation'] = 0.0
                vals['accumulated_qty'] = 0.0
        else:
            vals['average'] = (
                vals['product_qty'] and
                vals['inventory_valuation'] / vals['product_qty'] or
                vals['average'])
        return True

    def _get_stock_card_move_line_dict(self, row, vals):
        res = dict(
            date=row['date'],
            move_id=row['move_id'],
            stock_card_product_id=self.id,
            product_qty=vals['product_qty'],
            qty=vals['direction'] * row['product_qty'],
            move_valuation=vals['direction'] * vals['move_valuation'],
            inventory_valuation=vals['inventory_valuation'],
            average=vals['average'],
            cost_unit=vals['cost_unit'],
        )
        return res

    def _get_stock_card_move_line(self, row, vals):
        res = self._get_stock_card_move_line_dict(row, vals)
        vals['lines'][row['move_id']] = res
        return True

    def _get_average_by_move(self, product_id, row, vals):
        dst = row['dst_usage']
        src = row['src_usage']
        if dst == 'internal':
            vals['direction'] = 1
        else:
            vals['direction'] = -1

        qntval = self._get_quant_values(row['move_id'])

        # TODO: What is to be done with `procurement` & `view`

        if dst in ('customer', 'production', 'inventory', 'transit'):
            self._get_price_on_consumed(row, vals, qntval)

        elif dst in ('supplier',):
            self._get_price_on_supplier_return(row, vals, qntval)

        elif src in ('supplier', 'production', 'inventory', ):
            self._get_price_on_supplied(row, vals, qntval)

        elif src in ('customer', 'transit'):
            self._get_price_on_customer_return(row, vals, qntval)

        self._get_move_average(row, vals)

        self._get_stock_card_move_line(row, vals)
        return True

    def _pre_get_average_by_move(self, row, vals):
        vals['previous_qty'] = vals['product_qty']
        vals['previous_valuation'] = vals['inventory_valuation']
        vals['previous_average'] = vals['average']
        return True

    def _post_get_average_by_move(self, row, vals):
        if not vals['rewind']:
            if vals['previous_qty'] > 0 and vals['product_qty'] < 0:
                vals['prior_qty'] = vals['previous_qty']
                vals['prior_valuation'] = vals['previous_valuation']
                vals['prior_average'] = vals['previous_average']
            if vals['product_qty'] < 0 and vals['direction'] < 0:
                vals['accumulated_move'].append(row)
            elif vals['previous_qty'] < 0 and vals['direction'] > 0:
                vals['accumulated_move'].append(row)
                vals['rewind'] = True
                vals['old_queue'] = vals['queue'][:]
                vals['queue'] = vals['accumulated_move'][:]

                vals['product_qty'] = vals['prior_qty']
                vals['inventory_valuation'] = vals['prior_valuation']
                vals['future_average'] = vals['average']

                vals['accumulated_variation'] = 0.0
                vals['accumulated_qty'] = 0.0

        else:
            if not vals['queue']:
                vals['rewind'] = False
                vals['queue'] = vals['old_queue'][:]

            if vals['product_qty'] > 0:
                vals['accumulated_move'] = []

        return True

    def _stock_card_move_get_avg(self, product_id, vals, locations_ids=None):
        vals['move_ids'] = self._stock_card_move_history_get(
            product_id, locations_ids)
        vals['queue'] = vals['move_ids'][:]
        while vals['queue']:

            row = vals['queue'].pop(0)

            self._pre_get_average_by_move(row, vals)

            self._get_average_by_move(product_id, row, vals)

            self._post_get_average_by_move(row, vals)

        return True

    def _get_default_params(self, product_id, locations_ids=None):
        res = dict(
            product_qty=0.0,
            average=0.0,
            inventory_valuation=0.0,
            lines={},
            move_dict={},
            accumulated_variation=0.0,
            accumulated_qty=0.0,
            accumulated_move=[],
            rewind=False,
            prior_qty=0.0,
            prior_valuation=0.0,
        )
        if locations_ids:
            vals = self._stock_card_move_get(product_id)
            values = {}
            for row in vals['move_ids']:
                values.update(
                    {row['move_id']: vals['lines'][row['move_id']].copy()})
            res['global_val'] = values
        return res

    def _stock_card_move_get(self, product_id, locations_ids=None):
        self.stock_card_move_ids.unlink()

        vals = self._get_default_params(product_id, locations_ids)

        self._stock_card_move_get_avg(product_id, vals, locations_ids)

        res = []
        for row in vals['move_ids']:
            res.append(vals['lines'][row['move_id']])
        vals['res'] = res

        return vals

    def get_stock_card_date_range(self, product_id, locations_ids=None):
        vals = self._stock_card_move_get(product_id, locations_ids)
        data = []
        index = []
        for row in vals['move_ids']:
            data.append(vals['lines'][row['move_id']])
            index.append(vals['lines'][row['move_id']]['date'])

        return pd.DataFrame(data, index=index)

    def create_stock_card_lines(self, product_id, locations_ids=None):
        scm_obj = self.env['stock.card.move']
        vals = self._stock_card_move_get(product_id, locations_ids)
        for row in vals['move_ids']:
            scm_obj.create(vals['lines'][row['move_id']])

        return True

    def _get_avg_fields(self):
        return ['average']

    @api.model
    def get_average(self, res=None):
        dct = {}
        res = dict(res or {})
        for avg_fn in self._get_avg_fields():
            dct[avg_fn] = res.get(avg_fn, 0.0)
        return dct

    def get_qty(self, product_id):
        res = self._stock_card_move_get(product_id)
        return res.get('product_qty')

    @api.multi
    def action_view_moves(self):
        """This function returns an action that display existing invoices of given
        commission payment ids. It can either be a in a list or in a form view,
        if there is only one invoice to show.
        """
        self.ensure_one()
        ctx = self._context.copy()

        ir_model_obj = self.pool['ir.model.data']
        model, action_id = ir_model_obj.get_object_reference(
            self._cr, self._uid, 'stock_card', 'stock_card_move_action')
        action = self.pool[model].read(
            self._cr, self._uid, action_id, context=self._context)
        action['context'] = ctx
        # compute the number of invoices to display
        scm_ids = [scm_brw.id for scm_brw in self.stock_card_move_ids]
        # choose the view_mode accordingly
        if len(scm_ids) >= 1:
            action['domain'] = "[('id','in',[" + ','.join(
                [str(scm_id) for scm_id in scm_ids]
            ) + "])]"
        else:
            raise UserError(
                _('Asked Product has not Moves to show'))
        return action

    def _stock_card_move_history_get(self, product_id, locations_ids=None):
        product_obj = self.env['product.product']
        query = '''
            SELECT distinct
                sm.id AS move_id, sm.date, sm.product_id, prod.product_tmpl_id,
                sm.origin_returned_move_id AS origin_returned_move_id,
                sm.move_dest_id AS move_dest_id,
                sm.price_unit AS price_unit,
                sm.product_qty, sl_src.usage AS src_usage,
                sl_dst.usage AS dst_usage,
                ir_prop_cost.value_text AS cost_method,
                sm.date AS date
            FROM stock_move AS sm
            INNER JOIN
                stock_location AS sl_src ON sm.location_id = sl_src.id
            INNER JOIN
                stock_location AS sl_dst ON sm.location_dest_id = sl_dst.id
            INNER JOIN
                 product_product AS prod ON sm.product_id = prod.id
            INNER JOIN
                product_template AS ptemp ON prod.product_tmpl_id = ptemp.id
            INNER JOIN
                ir_property AS ir_prop_cost ON (
                    ir_prop_cost.res_id = 'product.template,' ||
                    ptemp.id::text and ir_prop_cost.name = 'cost_method')
            WHERE
                sm.state = 'done' -- Stock Move already DONE
                AND ir_prop_cost.value_text = 'average' -- Average Products
                AND sl_src.usage != sl_dst.usage -- No self transfers
                AND (
                    (sl_src.usage = 'internal' AND sl_dst.usage != 'internal')
                    OR (
                    sl_src.usage != 'internal' AND sl_dst.usage = 'internal')
                ) -- Actual incoming or outgoing Stock Moves
                AND sm.product_id = %s
                '''
        if locations_ids:
            query += self._cr.mogrify('''
                AND (sl_src.id IN %s or sl_dst.id IN %s)
            ''', (locations_ids, locations_ids))

        date = product_obj.browse(product_id).date_stock_card_border
        if date:
            query += self._cr.mogrify('''AND sm.date >= %s
                                      ''', (date,))

        query += '''ORDER BY sm.date'''
        self._cr.execute(query, (product_id,))
        return self._cr.dictfetchall()


class StockCardMove(models.TransientModel):
    _name = 'stock.card.move'

    stock_card_product_id = fields.Many2one(
        'stock.card.product', string='Stock Card Product')
    move_id = fields.Many2one('stock.move', string='Stock Moves')
    product_qty = fields.Float('Inventory Quantity')
    qty = fields.Float('Move Quantity')
    move_valuation = fields.Float(
        string='Move Valuation',
        digits=dp.get_precision('Account'),
        readonly=True)
    inventory_valuation = fields.Float(
        string='Inventory Valuation',
        digits=dp.get_precision('Account'),
        readonly=True)
    average = fields.Float(
        string='Average',
        digits=dp.get_precision('Account'),
        readonly=True)
    cost_unit = fields.Float(
        string='Unit Cost',
        digits=dp.get_precision('Account'),
        readonly=True)
    date = fields.Datetime(string='Date')
