# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from osv import fields, osv
from tools.translate import _
import decimal_precision as dp

class pedigree_serialization_manager(osv.osv_memory):
    _name = "pedigree.serialization.manager"
    _description = "Pedigree Serialization Manager"

    def default_get(self, cr, uid, fields, context=None):
        """ Get default values
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param fields: List of fields for default value
        @param context: A standard dictionary
        @return: Default values of fields
        """
        if context is None:
            context = {}
        res = super(pedigree_serialization_manager, self).default_get(cr, uid, fields, context=context)
        if context.get('active_id'):
            move = self.pool.get('stock.move').browse(cr, uid, context['active_id'], context=context)
            if 'product_id' in fields:
                res.update({'product_id': move.product_id.id})
            if 'product_uom' in fields:
                res.update({'product_uom': move.product_uom.id})
            if 'qty' in fields:
                res.update({'qty': move.product_qty})
            if 'location_id' in fields:
                res.update({'location_id': move.location_id.id})
        return res

    _columns = {
        'qty': fields.float('Quantity', digits_compute=dp.get_precision('Product UoM')),
        'product_id': fields.many2one('product.product', 'Product', required=True, select=True),
        'product_uom': fields.many2one('product.uom', 'UoM'),
        'psm':fields.text('Pedigree Serialization Manager'),
        #~ 'line_ids': fields.one2many('stock.move.split.lines', 'lot_id', 'Production Lots'),
        #~ 'line_exist_ids': fields.one2many('stock.move.split.lines.exist', 'lot_id', 'Production Lots'),
        #~ 'use_exist' : fields.boolean('Existing Lots', help="Check this option to select existing lots in the list below, otherwise you should enter new ones line by line."),
        'location_id': fields.many2one('stock.location', 'Source Location')
     }

    def split_lot(self, cr, uid, ids, context=None):
        """ To split a lot
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: An ID or list of IDs if we want more than one
        @param context: A standard dictionary
        @return:
        """
        if context is None:
            context = {}
        self.split(cr, uid, ids, context.get('active_ids'), context=context)
        return {'type': 'ir.actions.act_window_close'}
#~ 
    def split(self, cr, uid, ids, move_ids, context=None):
        #~ """ To split stock moves into production lot
        #~ @param self: The object pointer.
        #~ @param cr: A database cursor
        #~ @param uid: ID of the user currently logged in
        #~ @param ids: the ID or list of IDs if we want more than one
        #~ @param move_ids: the ID or list of IDs of stock move we want to split
        #~ @param context: A standard dictionary
        #~ @return:
        #~ """
        if context is None:
            context = {}
        inventory_id = context.get('inventory_id', False)
        prodlot_obj = self.pool.get('stock.production.lot')
        inventory_obj = self.pool.get('stock.inventory')
        move_obj = self.pool.get('stock.move')
        new_move = []
        
        for data in self.browse(cr, uid, ids, context=context):
            for move in move_obj.browse(cr, uid, move_ids, context=context):
                move_qty = move.product_qty
                quantity_rest = move.product_qty
                uos_qty_rest = move.product_uos_qty
                new_move = []
                total_move_qty = 0.0
                psm = data.psm
                if psm:
                    lines=psm.split('\n')
                    lines = list(set(lines))
                else:
                    lines=[]
                for line in lines:
                    quantity = 1
                    total_move_qty += quantity
                    if total_move_qty > move_qty:
                        precision = '%0.' + str(dp.get_precision('Product UoM')(cr)[1] or 0) + 'f'
                        raise osv.except_osv(_('Processing Error'), _('Processing quantity %s for %s is larger than the available quantity %s!')\
                                     % (precision % total_move_qty, move.product_id.name, precision % move_qty))
                    if quantity <= 0 or move_qty == 0:
                        continue
                    quantity_rest -= quantity
                    uos_qty = quantity / move_qty * move.product_uos_qty
                    uos_qty_rest = quantity_rest / move_qty * move.product_uos_qty
                    if quantity_rest < 0:
                        quantity_rest = quantity
                        break
                    default_val = {
                        'product_qty': quantity,
                        'product_uos_qty': uos_qty,
                        'state': move.state
                    }
                    if quantity_rest > 0:
                        current_move = move_obj.copy(cr, uid, move.id, default_val, context=context)
                        if inventory_id and current_move:
                            inventory_obj.write(cr, uid, inventory_id, {'move_ids': [(4, current_move)]}, context=context)
                        new_move.append(current_move)

                    if quantity_rest == 0:
                        current_move = move.id
                    prodlot_id = False
                    if not prodlot_id:
                        prodlot_id = prodlot_obj.create(cr, uid, {
                            'name': line,
                            'product_id': move.product_id.id},
                        context=context)

                    move_obj.write(cr, uid, [current_move], {'prodlot_id': prodlot_id, 'state':move.state})

                    update_val = {}
                    if quantity_rest > 0:
                        update_val['product_qty'] = quantity_rest
                        update_val['product_uos_qty'] = uos_qty_rest
                        update_val['state'] = move.state
                        move_obj.write(cr, uid, [move.id], update_val)

        return new_move

pedigree_serialization_manager()
