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
        self.create_move_variation(cr, uid, ids, context=context)
        return res

    def create_move_variation(self, cr, uid, ids, context={}):
        move_obj = self.pool.get('account.move')
        account_moves = []
        for production in self.browse(cr, uid, ids, context=context):
            for prod_variation in production.variation_ids:
                context['type'] = 'consumed'
                if prod_variation.product_id and\
                prod_variation.product_id.valuation == 'real_time' and\
                prod_variation.quantity != 0:
                    j_id, src_acc, dest_acc, reference_amount =\
                        self.get_journal_accounts(cr, uid, prod_variation,
                            production, context=context)
                    account_moves += [(j_id,
                        self.create_account_variation_move_line(
                        cr, uid, prod_variation, src_acc, dest_acc,
                        reference_amount))]

            for prod_variation in production.variation_finished_product_ids:
                context['type'] = 'produced'
                if prod_variation.product_id and\
                prod_variation.product_id.valuation == 'real_time' and\
                prod_variation.quantity != 0:
                    j_id, src_acc, dest_acc, reference_amount =\
                        self.get_journal_accounts(cr, uid, prod_variation,
                        production, context=context)
                    account_moves += [(j_id,
                        self.create_account_variation_move_line(
                        cr, uid, prod_variation, src_acc, dest_acc,
                        reference_amount))]

            if account_moves:
                for j_id, move_lines in account_moves:
                    move_obj.create(cr, uid,
                                    {
                                    'journal_id': j_id,
                                    'line_id': move_lines,
                                    'ref': 'PROD: ' + production.name})

        return True

    def get_journal_accounts(self, cr, uid, product, production, context={}):

        if not context:
            context = {}

        src_acc = False
        dest_acc = False

        if context.get('type', False) == 'consumed':
            if product.quantity > 0:
                if production.product_id.property_stock_production.valuation_in_account_id:
                    src_acc = production.product_id.property_stock_production.valuation_in_account_id.id
                if product.product_id.type == 'service':
                    dest_acc = product.product_id.categ_id.property_stock_valuation_account_id and\
                    product.product_id.categ_id.property_stock_valuation_account_id.id or False
                elif production.product_id.property_stock_production.variation_in_account_id:
                    dest_acc = production.product_id.property_stock_production.variation_in_account_id.id
                reference_amount = product.cost_variation

            if product.quantity < 0:
                if product.product_id.type == 'service':
                    src_acc = product.product_id.categ_id.property_stock_valuation_account_id and\
                    product.product_id.categ_id.property_stock_valuation_account_id.id or False
                elif production.product_id.property_stock_production.variation_in_account_id:
                    src_acc = production.product_id.property_stock_production.variation_in_account_id.id
                if production.product_id.property_stock_production.valuation_in_account_id:
                    dest_acc = production.product_id.property_stock_production.valuation_in_account_id.id
                reference_amount = product.cost_variation*-1

        if context.get('type', False) == 'produced':
            if product.quantity > 0:
                if production.product_id.property_stock_production.valuation_out_account_id:
                    src_acc = production.product_id.property_stock_production.variation_out_account_id.id
                if production.product_id.property_stock_production.variation_out_account_id:
                    dest_acc = production.product_id.property_stock_production.valuation_out_account_id.id
                reference_amount = product.cost_variation
            if product.quantity < 0:
                if production.product_id.property_stock_production.variation_out_account_id:
                    src_acc = production.product_id.property_stock_production.valuation_out_account_id.id
                if production.product_id.property_stock_production.valuation_out_account_id:
                    dest_acc = production.product_id.property_stock_production.variation_out_account_id.id
                reference_amount = product.cost_variation*-1

        journal_id = product.product_id.categ_id.property_stock_journal.id
        if not src_acc or not dest_acc:
            raise osv.except_osv(_('Error!'), 
                    _('There is no account defined for this location: "%s" ') %
                    (production.product_id.property_stock_production.name,))

        if not journal_id:
            raise osv.except_osv(_('Error!'),
                _('There is no journal defined on the product category:\
                    "%s" (id: %d)') %
                (product.product_id.categ_id.name,
                    product.product_id.categ_id.id,))

        return journal_id, src_acc, dest_acc, reference_amount

    def create_account_variation_move_line(self, cr, uid, prod_variation,
            src_account_id, dest_account_id, reference_amount, context=None):
        debit_line_vals = {
            'name': 'PROD: ' + prod_variation.production_id.name + ' - ' +\
                            (prod_variation.product_id and
                            prod_variation.product_id.name or ''),
                    'product_id': prod_variation.product_id and
                            prod_variation.product_id.id or False,
                    'quantity': prod_variation.quantity,
            #                   'ref': 'prueba',
                    'date': time.strftime('%Y-%m-%d'),
#                    'partner_id': partner_id,
                    'debit': reference_amount,
                    'account_id': dest_account_id,
        }
        credit_line_vals = {
            'name': 'PROD: ' + prod_variation.production_id.name + ' - ' +\
                (prod_variation.product_id and
                prod_variation.product_id.name or ''),
            'product_id': prod_variation.product_id and
                prod_variation.product_id.id or False,
            'quantity': prod_variation.quantity,
    #                 'ref': 'prueba',
            'date': time.strftime('%Y-%m-%d'),
    #                   'partner_id': partner_id,
            'credit': reference_amount,
            'account_id': src_account_id,
        }

        return [(0, 0, debit_line_vals), (0, 0, credit_line_vals)]

#    def action_production_end(self, cr, uid, ids):
 #       res  = super(mrp_production, self).action_production_end(cr, uid, ids)
  #      self.action_finish(cr, uid, ids)
   #     return res


class stock_move(osv.Model):
    _inherit = 'stock.move'

    def _create_account_move_line(self, cr, uid, move, src_account_id,
                                dest_account_id, reference_amount,
                                reference_currency_id, context=None):
        res = super(stock_move, self)._create_account_move_line(
            cr, uid, move, src_account_id, dest_account_id, reference_amount,
            reference_currency_id, context=context)
        for lin in res:
            lin[2]['name'] = move.name + ' - ' + (
                move.product_id and move.product_id.name or '')
        return res
