# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 Vauxoo - http://www.vauxoo.com
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
from openerp.osv import fields, osv
from openerp.tools.translate import _


class account_move_line(osv.Model):
    _inherit = "account.move.line"

    """
    """

    _columns = {
        'sm_id': fields.many2one('stock.move', 'Stock move ID'),
        'location_id':fields.related('sm_id', 'location_id', string='Source Location',
            type='many2one', relation='stock.location', store=True, help='Location Move Source'),
        'location_dest_id':fields.related('sm_id', 'location_dest_id',
            type='many2one', string='Destination Location', relation='stock.location', store=True,
            help="Location Move Destination")
    }


class account_move(osv.Model):
    _inherit = "account.move"

    """
    """
    def _get_sm(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for id in ids:
            cr.execute(
                '''SELECT move_id,
                          sm_id
                   FROM account_move_line
                   WHERE move_id = %s LIMIT 1 ''' % (id,))
            if cr.rowcount:
                id, sm_id = cr.fetchall()[0]
                res[id] = sm_id
            else:
                res[id] = False
        return res

    _columns = {
        'sm_id': fields.function(_get_sm, method=True, type='many2one',
                                 relation='stock.move',
                                 string='Stock move ID', store=True),
    }


class stock_move(osv.Model):
    _inherit = "stock.move"

    """
    """

    def _get_am(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for id in ids:
            cr.execute(
                '''SELECT sm_id,
                   move_id
                   FROM account_move_line
                   WHERE sm_id = %s LIMIT 1 ''' % (id,))
            if cr.rowcount:
                id, am_id = cr.fetchall()[0]
                res[id] = am_id
            else:
                res[id] = False
        return res

    _columns = {
        'am_id': fields.function(_get_am, method=True, type='many2one',
                                 relation='account.move',
                                 string='Account move ID', store=True),
    }

    def _create_account_move_line(self, cr, uid, move, src_account_id,
                                  dest_account_id,
                                  reference_amount, reference_currency_id,
                                  context=None):
        res = super(stock_move, self).\
            _create_account_move_line(cr, uid, move, src_account_id,
                                      dest_account_id,
                                      reference_amount,
                                      reference_currency_id,
                                      context=context)
        for line in res:
            line[2]['sm_id'] = move.id
        return res
