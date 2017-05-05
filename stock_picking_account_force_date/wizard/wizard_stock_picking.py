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
from osv import osv, fields

class wizard_stock_picking(osv.TransientModel):
    _name='wizard.stock.picking'
    _columns={
        'new_date' : fields.datetime('New Date', required=True),
        'stock_picking_ids': fields.many2many('stock.picking', 
            'stock_picking_rel', 'temp_id', 'picking_id', 'Pickings'),
    }
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None:context = {}
        picking_ids = context['active_ids']
        res = super(wizard_stock_picking, self).default_get(cr, uid, 
            fields, context=context)
        res.update({
            'stock_picking_ids': picking_ids or False,
        })
        return res

    def wizard_picking_change_date(self, cr, uid, ids, context=None):
        """ Calls the function picking_change_date to change the date.
        @return: {}
        """
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, [])
        picking_ids = data[0]['stock_picking_ids']
        new_date = data[0]['new_date'] or False
        self.pool.get('stock.picking').picking_change_date(cr, uid, 
            picking_ids, new_date, context=context)
        return {}
