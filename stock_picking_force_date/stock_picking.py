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

class stock_picking(osv.Model):
    _inherit = 'stock.picking'

    def picking_change_date(self, cr, uid, ids, new_date, context={}):
        """ Changes date of picking with every move.
        @return: {}
        """
        if context is None:
            context = {}
        move_ids = []
        for picking in self.browse(cr, uid, ids, context=context):
             if picking.state not in ('cancel'):
                picking.write({'date': new_date})
                move_ids = [x.id for x in picking.move_lines if x.state not in ('cancel')]
                print move_ids
                self.pool.get('stock.move').stock_move_change_date(cr, uid, 
                    move_ids, new_date, context=context)
        return {}
    
class stock_move(osv.Model):
    _inherit = 'stock.move'
    
    def stock_move_change_date(self, cr, uid, ids, new_date, context={}):
        if context is None:
            context = {}
        for move in self.pool.get('stock.move').browse(cr, uid, 
            ids, context=context):
            if move.state not in ('cancel'):
                move.write({'date': new_date})
        return {}
