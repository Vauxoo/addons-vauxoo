# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: fernandoL (fernando_ld@vauxoo.com)
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


class account_move_line(osv.Model):
    _inherit = "account.move.line"

    """
    """

    _columns = {
        'production_id': fields.many2one('mrp.production', 'Production ID'),
        'stock_move_id': fields.many2one('stock.move', 'Stock move ID'),
    }


class account_move(osv.Model):
    _inherit = "account.move"

    """
    """

    _columns = {
        'production_id': fields.many2one('mrp.production', 'Production ID'),
        'stock_move_id': fields.many2one('stock.move', 'Stock move ID'),
    }


class stock_move(osv.Model):
    _inherit = "stock.move"

    """
    """

    def _create_account_move_line(self, cr, uid, move, src_account_id,
            dest_account_id, reference_amount, reference_currency_id,
            context=None):
        res = super(stock_move, self)._create_account_move_line(
            cr, uid, move, src_account_id, dest_account_id, reference_amount,
            reference_currency_id, context=context)
        cr.execute(
            'SELECT production_id FROM mrp_production_move_ids\
            WHERE move_id = %s', (move.id,))
        result = cr.dictfetchall()
        for line in res:
            line[2]['stock_move_id'] = move.id
            line[2]['production_id'] = move.production_id and\
                move.production_id.id or (
                    result and result[0]['production_id'] or False)
        return res

    def action_consume(self, cr, uid, ids, product_qty,
                       location_id=False, lot_id=False, context=None):
        account_move_line_pool = self.pool.get('account.move.line')
        res = super(stock_move, self).action_consume(
            cr, uid, ids, product_qty, location_id=location_id,
            lot_id=lot_id, context=context)
        for move_id in res:
            cr.execute(
                'SELECT production_id FROM mrp_production_move_ids\
                WHERE move_id = %s', (move_id,))
            result = cr.dictfetchall()
            account_move_line_id = account_move_line_pool.search(
                cr, uid, [('stock_move_id', '=', move_id)])
            if result and account_move_line_id:
                account_move_line_pool.write(cr, uid, account_move_line_id, {
                    'production_id': result[0]['production_id']})
        return res
