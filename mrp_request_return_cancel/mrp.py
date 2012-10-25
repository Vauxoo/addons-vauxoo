# -*- coding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: julio (fernando_ld@vauxoo.com)
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
from osv import osv, fields
from tools.translate import _
from datetime import datetime
import netsvc
    
class mrp_production(osv.osv):
    _inherit = "mrp.production"
    
    def action_cancel(self, cr, uid, ids, context=None):

        if context is None:
            context = {}
            
        move_obj = self.pool.get('stock.move')
        request_return_picking_ids = []
        for production in self.browse(cr, uid, ids, context=context):
            if production.picking_ids:
                for line in production.picking_ids:
                    for entry_line in line.move_lines:
                        request_return_picking_ids.append(entry_line.id)
                move_obj.action_cancel(cr, uid, request_return_picking_ids)
        return super(mrp_production, self).action_cancel(cr, uid, ids, context=context)
    
mrp_production()