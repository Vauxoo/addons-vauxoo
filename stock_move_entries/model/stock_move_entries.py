# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: julio (julio@vauxoo.com)
#              Luis Ernesto García Medina (ernesto_gm@vauxoo.com)
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


class AccountMoveLine(osv.Model):
    _inherit = "account.move.line"

    """
    """

    _columns = {
        'sm_id': fields.many2one('stock.move', 'Stock move'),
    }


class StockMove(osv.Model):
    _inherit = "stock.move"

    """
    """

    _columns = {
        'aml_ids': fields.one2many(
            'account.move.line', 'sm_id', 'Account move Lines',
            domain=[('account_id.reconcile', '=', True)]),
        'aml_all_ids': fields.one2many(
            'account.move.line', 'sm_id', 'Account move Lines'),
    }


class StockQuant(osv.Model):
    _inherit = "stock.quant"

    def _prepare_account_move_line(self, cr, uid, move, qty, cost,
                                   credit_account_id, debit_account_id,
                                   context=None):
        res = super(StockQuant, self)._prepare_account_move_line(
            cr, uid, move, qty, cost, credit_account_id, debit_account_id,
            context)
        for line in res:
            line[2]['sm_id'] = move.id
        return res
