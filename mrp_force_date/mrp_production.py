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

class mrp_production(osv.Model):
    _inherit = 'mrp.production'

    def mrp_change_date(self, cr, uid, ids, new_date, context={}):
        """ Changes date of Mrp.
        @return: {}
        """
        if context is None:
            context = {}
        picking_ids = []
        move_ids = []
        moves = []
        for mrp_id in self.browse(cr, uid, ids, context=context):
             if mrp_id.state not in ('cancel', 'draft'):
                mrp_id.write({'date_planned': new_date})
                picking_ids.append(self.pool.get('stock.picking').search(
                cr, uid, [('id', '=', mrp_id.picking_id.id)], 
                    context=context)[0])
                moves = [x.id for x in mrp_id.move_lines if x.state not in ('cancel', 'draft')]
                move_ids.extend(moves)
                moves = [x.id for x in mrp_id.move_lines2 if x.state not in ('cancel', 'draft')]
                move_ids.extend(moves)
                moves = [x.id for x in mrp_id.move_created_ids if x.state not in ('cancel', 'draft')]
                move_ids.extend(moves)
                moves = [x.id for x in mrp_id.move_created_ids2 if x.state not in ('cancel', 'draft')]
                move_ids.extend(moves)
        self.pool.get('stock.picking').picking_change_date(cr, uid, 
            picking_ids, new_date, context=context)
        self.pool.get('stock.move').stock_move_change_date(cr, uid, 
            move_ids, new_date, context=context)
        return {}
