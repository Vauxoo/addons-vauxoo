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

class account_move_line(osv.osv):
    _inherit = "account.move.line"
    
    """
    """
    
    _columns = {
        'sm_id': fields.many2one('stock.move', 'Stock move ID'),
        'location_id' : fields.many2one('stock.location', 'Location Move', help="Location Move Source"),
        'location_dest_id' : fields.many2one('stock.location', 'Location Move', help="Location Move Destination")
    }

account_move_line()

class account_move(osv.osv):
    _inherit = "account.move"
    
    """
    """
    _columns = {
        'sm_id': fields.many2one('stock.move', 'Stock move ID'),
    }

account_move()

class stock_move(osv.osv):
    _inherit = "stock.move"
    
    """
    """
    
    _columns = {
        'am_id' : fields.many2one('account.move', 'Account move ID')
    }
    def _create_account_move_line(self, cr, uid, move, src_account_id, dest_account_id, reference_amount, reference_currency_id, context=None):
        res = super(stock_move,self)._create_account_move_line(cr, uid, move, src_account_id, dest_account_id, reference_amount, reference_currency_id, context=context)
        for line in res:
            line[2]['sm_id'] = move.id
            line[2]['location_id'] = move.location_id.id
            line[2]['location_dest_id'] = move.location_dest_id.id
        return res

stock_move()