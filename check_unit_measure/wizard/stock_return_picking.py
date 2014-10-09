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

from openerp import netsvc
import time

from openerp.osv import osv, fields
from openerp.tools.translate import _


class stock_return_picking_memory(osv.TransientModel):
    _inherit = "stock.return.picking.memory"

    _columns = {
        'uom_id': fields.many2one('product.uom', string="UOM", required=True),

    }


class stock_return_picking(osv.TransientModel):
    _inherit = 'stock.return.picking'

    def default_get(self, cr, uid, fields, context=None):
        """
         To get default values for the object.
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param fields: List of fields for which we want default values
         @param context: A standard dictionary
         @return: A dictionary with default values for all field in ``fields``
        """
        result1 = []
        if context is None:
            context = {}
        res = super(stock_return_picking, self).default_get(
            cr, uid, fields, context=context)
        record_id = context and context.get('active_id', False) or False
        pick_obj = self.pool.get('stock.picking')
        pick = pick_obj.browse(cr, uid, record_id, context=context)
        if pick:
            if 'invoice_state' in fields:
                if pick.invoice_state == 'invoiced':
                    res.update({'invoice_state': '2binvoiced'})
                else:
                    res.update({'invoice_state': 'none'})
            return_history = self.get_return_history(
                cr, uid, record_id, context)
            for line in pick.move_lines:
                qty = line.product_qty - return_history.get(line.id, 0)
                if qty > 0:
                    result1.append(
                        {'product_id': line.product_id.id,
                            'uom_id': line.product_uom.id,
                            'quantity': qty,
                            'move_id': line.id,
                            'prodlot_id': line.prodlot_id and
                         line.prodlot_id.id or False})
            if 'product_return_moves' in fields:
                res.update({'product_return_moves': result1})
        return res

    def create_returns(self, cr, uid, ids, context=None):
        """
         Creates return picking.
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param ids: List of ids selected
         @param context: A standard dictionary
         @return: A dictionary which of fields with values.
        """
        if context is None:
            context = {}
        context.update({'pass_check': True})
        record_id = context and context.get('active_id', False) or False
        move_obj = self.pool.get('stock.move')
        pick_obj = self.pool.get('stock.picking')
        uom_obj = self.pool.get('product.uom')
        data_obj = self.pool.get('stock.return.picking.memory')
        wf_service = netsvc.LocalService("workflow")
        pick = pick_obj.browse(cr, uid, record_id, context=context)
        data = self.read(cr, uid, ids[0], context=context)
        date_cur = time.strftime('%Y-%m-%d %H:%M:%S')
        set_invoice_state_to_none = True
        returned_lines = 0

#        Create new picking for returned products
        if pick.type == 'out':
            new_type = 'in'
        elif pick.type == 'in':
            new_type = 'out'
        else:
            new_type = 'internal'
        seq_obj_name = 'stock.picking.' + new_type
        new_pick_name = self.pool.get('ir.sequence').get(cr, uid, seq_obj_name)
        new_picking = pick_obj.copy(cr, uid, pick.id, {
            'name': _('%s-%s-return') % (new_pick_name, pick.name),
            'move_lines': [],
            'state': 'draft',
            'type': new_type,
            'date': date_cur,
            'invoice_state': data['invoice_state'],
        }, context=context)

        val_id = data['product_return_moves']
        for v in val_id:
            data_get = data_obj.browse(cr, uid, v, context=context)
            mov_id = data_get.move_id.id
            uom_id = data_get.uom_id.id
            new_qty = data_get.quantity
            move = move_obj.browse(cr, uid, mov_id, context=context)
            new_location = move.location_dest_id.id
            returned_qty = move.product_qty
            for rec in move.move_history_ids2:
                returned_qty -= rec.product_qty

            if returned_qty != new_qty:
                set_invoice_state_to_none = False
            if new_qty:
                returned_lines += 1
                new_move = move_obj.copy(cr, uid, move.id, {
                    'product_qty': new_qty,
                    'product_uos_qty': uom_obj._compute_qty(cr, uid,
                                        move.product_uom.id, new_qty,
                                        move.product_uos.id),
                    'product_uom': uom_id,
                    'picking_id': new_picking,
                    'state': 'draft',
                    'location_id': new_location,
                    'location_dest_id': move.location_id.id,
                    'date': date_cur,
                }, context=context)
                move_obj.write(cr, uid, [move.id], {
                               'move_history_ids2': [(4, new_move)]},
                               context=context)
        if not returned_lines:
            raise osv.except_osv(_('Warning!'), _(
                "Please specify at least one non-zero quantity."))

        if set_invoice_state_to_none:
            pick_obj.write(cr, uid, [pick.id], {
                           'invoice_state': 'none'}, context=context)
        wf_service.trg_validate(
            uid, 'stock.picking', new_picking, 'button_confirm', cr)
        pick_obj.force_assign(cr, uid, [new_picking], context)
        # Update view id in context, lp:702939
        model_list = {
            'out': 'stock.picking.out',
            'in': 'stock.picking.in',
            'internal': 'stock.picking',
        }
        return {
            'domain': "[('id', 'in', ["+str(new_picking)+"])]",
            'name': _('Returned Picking'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': model_list.get(new_type, 'stock.picking'),
            'type': 'ir.actions.act_window',
            'context': context,
        }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
