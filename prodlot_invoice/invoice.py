#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Juan Carlos Funes(juan@vauxoo.com)
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
################################################################################

from osv import fields, osv, orm
from tools.translate import _

class account_invoice_line(osv.osv):
    _inherit = "account.invoice.line"

    def onchange_prodlot_id(self, cr, uid, ids, product_id, context=None):
        res = {}
        if not product_id:
            res['value'] = {'prodlot_id': False }
        return res


    def _check_len_move(self cr, uid, ids, field_name, args, context={}):
        res = {}
        for p in self.browse(cr,uid,ids,context=context):
            print p
            moves = [move for move in p.product_id if move.track_outgoing==True]
            print moves
            res[p.id]=len(moves)
        return res

    _columns = {
        'prodlot_id': fields.many2one('stock.production.lot', 'Production Lot', domain="[('product_id','=',product_id)]"),
        'check_prodlot' : fields.function(_check_len_move, string='check', type='integer'),
}

account_invoice_line()
