#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: javier@vauxoo.com
#    Planified by: Nhomar Hernandez
#    Audited by: Vauxoo C.A.
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##########################################################################

from openerp.osv import osv, fields
from openerp.tools.translate import _

import openerp.netsvc as netsvc


class picking_valued(osv.TransientModel):
    logger = netsvc.Logger()
    _name = "picking.valued"
    _columns = {
        'type': fields.selection([
            ('entrega', 'Nota de Entrega (Con Precios)'),
            ('despacho', 'Nota de Entrega (Sin Precios)'),
        ], 'Type', required=True, select=True),
        'sure': fields.boolean('Are you sure?'),
        'sure2': fields.boolean('Are you sure?'),
        'sure3': fields.boolean('Are you sure?'),
        'sure4': fields.boolean('Are you sure?'),
        'note': fields.char('Note', size=256, required=False, readonly=False),
        'note2': fields.char('Note', size=256, required=False, readonly=False),
        'reason': fields.selection([
            ('rep', 'Reparación'),
            ('tdep', 'Traslado a depósito'),
            ('talmo', 'Traslado almacenes o bodegas de otros'),
            ('talmp', 'Traslado almacenes o bodegas propios'),
            ('tdis', 'Traslado para su distribución'),
            ('otr', 'Otros')
        ], 'Reason', select=True),
        'nro': fields.char('Number', 32, readonly=True),
    }

    _defaults = {
        'type': 'entrega'
    }

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
        if context is None:
            context = {}
        res = super(picking_valued, self).default_get(
            cr, uid, fields, context=context)
        record_id = context and context.get('active_id', False) or False
        pick_obj = self.pool.get('picking.valued')
        pick = pick_obj.browse(cr, uid, record_id, context=context)
        if pick:
            for field in ('type', 'note', 'nro'):
                if context.get(field, False):
                    res[field] = context[field]
                    if field == 'note':
                        res['note2'] = context[field]
        return res

    def action_start(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        data_pool = self.pool.get('ir.model.data')
        obj = self.browse(cr, uid, ids[0])
        if obj.sure == False:
            raise osv.except_osv(_('Alert !'), _('Check the box!!!'))
        context.update({'type': obj.type})

        action = {}
        action_model, action_id = data_pool.get_object_reference(
            cr, uid, 'l10n_ve_stock', "action_pick_trans")
        if action_model:
            action_pool = self.pool.get(action_model)
            action = action_pool.read(cr, uid, action_id, context=context)
            action.update({'context': context})

        return action

    def action_trans(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        data_pool = self.pool.get('ir.model.data')
        obj = self.browse(cr, uid, ids[0])
        if obj.sure2 == False:
            raise osv.except_osv(_('Alert !'), _('Check the box!!!'))

        context.update({'note': obj.note})
        if not context['note']:
            return self.action_number(cr, uid, ids, context=context)

        action = {}
        action_model, action_id = data_pool.get_object_reference(
            cr, uid, 'l10n_ve_stock', "action_pick_note")
        if obj.type == 'despacho':
            action_model, action_id = data_pool.get_object_reference(
                cr, uid, 'l10n_ve_stock', "action_pick_reason")
        if action_model:
            action_pool = self.pool.get(action_model)
            action = action_pool.read(cr, uid, action_id, context=context)
            action.update({'context': context})

        return action

    def make_nro(self, cr, uid, ids, context=None):
        cr.execute('SELECT id, number '
                   'FROM stock_picking '
                   'WHERE id IN  %s', (tuple(ids),))

        for (id, number) in cr.fetchall():
            if not number:
                number = self.pool.get('ir.sequence').get(
                    cr, uid, 'stock.valued')
            cr.execute('UPDATE stock_picking SET number=%s '
                       'WHERE id=%s', (number, id))

        return number

    def action_number(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        data_pool = self.pool.get('ir.model.data')
        obj = self.browse(cr, uid, ids[0])
        comment = obj.note2 or obj.note
        razon = getattr(obj, 'reason')
        motiv = {
            'rep': 'Reparación',
            'tdep': 'Traslado a depósito',
            'talmo': 'Traslado almacenes o bodegas de otros',
            'talmp': 'Traslado almacenes o bodegas propios',
            'tdis': 'Traslado para su distribución',
            'otr': 'Otros'
        }

        record_id = context and context.get('active_id', False) or False
        pick_obj = self.pool.get('stock.picking')
        number = self.make_nro(cr, uid, [record_id], context)
        if razon:
            comment += '\n' + motiv[razon]
        pick_obj.write(cr, uid, [record_id], {'note': comment})

        context.update({'nro': number})
        action = {}
        action_model, action_id = data_pool.get_object_reference(
            cr, uid, 'l10n_ve_stock', "action_pick_end")
        if action_model:
            action_pool = self.pool.get(action_model)
            action = action_pool.read(cr, uid, action_id, context=context)
            action.update({'context': context})

        return action



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
