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
from openerp.osv import osv


class mrp_production(osv.Model):
    _inherit = 'mrp.production'

    def create_account_variation_move_line(self, cr, uid, prod_variation,
        src_account_id, dest_account_id, reference_amount, context=None):
        res = super(mrp_production, self).create_account_variation_move_line(
            cr, uid, prod_variation, src_account_id, dest_account_id,
            reference_amount, context=context)
        for lin in res:
            lin[2][
                'production_id'] = prod_variation.production_id and\
                                    prod_variation.production_id.id or False
        return res

    def action_cancel(self, cr, uid, ids, context=None):
        account_move_line = self.pool.get('account.move.line')
        account_move = self.pool.get('account.move')

        if context is None:
            context = {}

        move_obj = self.pool.get('stock.move')
        result = {}
        for production in self.browse(cr, uid, ids, context=context):
            account_move_line_id = account_move_line.search(
                cr, uid, [('production_id', '=', production.id)])
            for move_line in account_move_line.browse(cr, uid,
                                        account_move_line_id, context=context):
                result.setdefault(move_line.move_id.id, production.id)
                account_move_line.unlink(cr, uid, [move_line.id])
        for lin in result.items():
            account_production = account_move.browse(
                cr, uid, lin[0], context=context)
            if len(account_production.line_id) == 0:
                try:
                    account_move.button_cancel(
                        cr, uid, [lin[0]], context=context)
                except:
                    pass
                account_move.unlink(cr, uid, [lin[0]])
        return super(mrp_production, self).action_cancel(cr, uid, ids,
                                                            context=context)
