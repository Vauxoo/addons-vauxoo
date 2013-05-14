# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: Juan Carlos Funes(juan@vauxoo.com)
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
import time
from datetime import datetime
from tools.translate import _

class stock_picking(osv.Model):
    _inherit = 'stock.picking'

    def picking_change_date(self, cr, uid, ids, new_date, context={}):
        """ Changes date of picking with every move.
        @return: {}
        """
        if context is None:
            context = {}
        move_ids = []
        move_lines_ids = []
        account_move_ids = []
        for picking in self.browse(cr, uid, ids, context=context):
             if picking.state not in ('cancel'):
                picking.write({'date': new_date})
                move_ids = [x.id for x in picking.move_lines if x.state 
                    not in ('cancel')]
                self.pool.get('stock.move').stock_move_change_date(cr, 
                    uid, move_ids, new_date, context=context)
                move_lines_ids = self.pool.get('account.move.line').search(
                cr, uid, [('stock_move_id', 'in', move_ids)], context=context)
                for move_line in self.pool.get('account.move.line').browse(
                    cr, uid, move_lines_ids, context=context):
                    account_move_ids.append(move_line.move_id.id)
                account_move_ids = list(set(account_move_ids))
                self.pool.get('account.move.line').\
                    account_move_line_change_date(cr, uid, move_lines_ids,
                    new_date, context=context)
                self.pool.get('account.move').account_move_change_date(
                    cr, uid, account_move_ids, new_date, context=context)
        return {}
    
class stock_move(osv.Model):
    _inherit = 'stock.move'
    
    def stock_move_change_date(self, cr, uid, ids, new_date, context={}):
        if context is None:
            context = {}
        for move in self.browse(cr, uid, ids, context=context):
            if move.state not in ('cancel', 'draft'):
                move.write({'date': new_date})
        return {}

class account_move_line(osv.Model):
    _inherit = 'account.move.line'
    
    def account_move_line_change_date(self, cr, uid, ids, new_date, context={}):
        if context is None:
            context = {}
        stock_move_date = datetime.strptime(new_date,
            '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
        period_id = self.pool.get('account.period').search(cr, uid, 
            [('date_start', '<=', stock_move_date), ('date_stop', '>=',
                stock_move_date), ('special', '=', False)], context=context)
        for move_line in self.browse(cr, uid, ids, context=context):
            if move_line.state not in ('cancel'):
                if not period_id:
                    raise osv.except_osv(_('No Period For This Date !'),
                    _("You must define a period of type special = False!") )
                else:
                    move_line.write({'date': new_date, 'period_id':
                    period_id and period_id[0] or False})
        return {}
        
class account_move(osv.Model):
    _inherit = 'account.move'
    
    def account_move_change_date(self, cr, uid, ids, new_date, context={}):
        if context is None:
            context = {}
        stock_move_date = datetime.strptime(new_date,
            '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
        period_id = self.pool.get('account.period').search(cr, uid, 
            [('date_start', '<=', stock_move_date), ('date_stop', '>=',
                stock_move_date), ('special', '=', False)], context=context)
        for move in self.browse(cr, uid, ids, context=context):
            if move.state not in ('cancel'):
                if not period_id:
                    raise osv.except_osv(_('No Period For This Date !'),
                    _("You must define a period of type special = False!"))
                else:
                    move.write({'date': new_date, 'period_id': 
                    period_id and period_id[0] or False})
        return {}
