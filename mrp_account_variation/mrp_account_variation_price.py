# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: julio (julio@vauxoo.com)
############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import osv, fields
from openerp.tools.translate import _

import openerp.netsvc as netsvc
import time


class mrp_production(osv.Model):
    _inherit = 'mrp.production'

    def action_finish(self, cr, uid, ids, context={}):
        res = super(mrp_production, self).action_finish(
            cr, uid, ids, context=context)
        self.create_move_variation_price(cr, uid, ids, context=context)
        return res

    def create_move_variation_price(self, cr, uid, ids, context={}):
        move_obj = self.pool.get('account.move')
        product_uom_pool = self.pool.get('product.uom')
        for production in self.browse(cr, uid, ids, context=context):
            if production.product_id.valuation == 'real_time':
                account_moves = []
                total_product_consumed = 0.0
                total_product_finished = 0.0
                for prod_consumed in production.product_lines:
                    product_consumed = product_uom_pool._compute_qty(
                        cr, uid, prod_consumed.product_uom.id,
                        prod_consumed.product_qty,
                        to_uom_id=prod_consumed.product_id.uom_id.id)
                    total_product_consumed += product_consumed * \
                        prod_consumed.product_id.standard_price
                for prod_finished in production.pt_planified_ids:
                    product_finished = product_uom_pool._compute_qty(
                        cr, uid, prod_finished.product_uom.id,
                        prod_finished.quantity,
                        to_uom_id=prod_finished.product_id.uom_id.id)
                    total_product_finished += product_finished * \
                        prod_finished.product_id.standard_price
                if production.product_id.property_stock_production:
                    if total_product_consumed > total_product_finished:
                        if production.product_id.property_stock_production.property_account_in_production_price_difference:
                            src_account_id = production.product_id.property_stock_production.valuation_out_account_id.id
                            dest_account_id = production.product_id.property_stock_production.property_account_in_production_price_difference.id
                            reference_amount = (
                                total_product_consumed -\
                                total_product_finished)
                            journal_id = production.product_id.categ_id.property_stock_journal.id
                            account_moves = [(journal_id,
                                self.create_account_variation_price_move_line(
                                    cr, uid, production, src_account_id,
                                    dest_account_id, reference_amount,
                                    context=None))]
                    if total_product_consumed < total_product_finished:
                        if production.product_id.property_stock_production.property_account_out_production_price_difference:
                            src_account_id = production.product_id.property_stock_production.property_account_out_production_price_difference.id
                            dest_account_id = production.product_id.property_stock_production.valuation_in_account_id.id
                            reference_amount = (
                                total_product_consumed -\
                                total_product_finished)*-1
                            journal_id = production.product_id.categ_id.property_stock_journal.id
                            account_moves = [(journal_id,
                                self.create_account_variation_price_move_line(
                                    cr, uid, production, src_account_id,
                                    dest_account_id, reference_amount,
                                    context=None))]

                if account_moves:
                    for j_id, move_lines in account_moves:
                        move_obj.create(cr, uid,
                                        {
                                        'journal_id': j_id,
                                        'line_id': move_lines,
                                        'ref': 'PROD: ' + production.name +\
                                            ' - ' + _('Deflection  by\
                                            difference on consume RM vs FP')})
        return True

    def create_account_variation_price_move_line(self, cr, uid, production,
                                                    src_account_id,
                                                    dest_account_id,
                                                    reference_amount,
                                                    context=None):
        debit_line_vals = {
            'name': 'PROD: ' + production.name or '',
                    'date': time.strftime('%Y-%m-%d'),
                    'debit': reference_amount,
                    'account_id': dest_account_id,
                    'production_id': production.id
        }
        credit_line_vals = {
            'name': 'PROD: ' + production.name or '',
                    'date': time.strftime('%Y-%m-%d'),
                    'credit': reference_amount,
                    'account_id': src_account_id,
                    'production_id': production.id
        }

        return [(0, 0, debit_line_vals), (0, 0, credit_line_vals)]
