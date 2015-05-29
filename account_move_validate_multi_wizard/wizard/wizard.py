# -*- encoding: utf-8 -*-
#
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
#
#    Coded by: Jorge Naranajo <jorge_nr@vauxoo.com>
#
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
#


from openerp.osv import fields, osv


class account_move_multi_wizard(osv.TransientModel):
    _name = 'account.move.multi.wizard'

    def default_get(self, cr, uid, fields, context=None):
        if not context:
            context = {}
        moves = context.get('active_ids', False)
        res = super(account_move_multi_wizard, self).default_get(
            cr, uid, fields, context=context)
        res.update({'account_move_ids': moves})
        return res

    _columns = {
        'account_move_ids': fields.many2many('account.move',
                                             'account_move_wizard_rel', 'wiz_id', 'move_id'),
        'result': fields.text('Result'),
    }

    def validate_moves(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        lista = []
        obj_account_move = self.pool.get('account.move')
        for form in self.browse(cr, uid, ids, context=context):
            for move in form.account_move_ids:
                try:
                    obj_account_move.button_validate(
                        cr, uid, [move.id], context=context)
                    cr.commit()
                except:
                    lista.append(move.id)
        if lista:
            __, xml_id = self.pool.get('ir.model.data').get_object_reference(
                cr, uid, 'account_move_validate_multi_wizard', 'account_move_validate_multi_wizard_unbalance')
            context.update(
                {'default_result': '''You cannot validate a non-balanced entry. Make sure you have configured payment terms properly.
The latest payment term line should be of the "Balance" type. \n\n In journal entries: %s''' % (lista)})
            return {
                'res_model': 'account.move.multi.wizard',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': xml_id,
                'context': context,
                'type': 'ir.actions.act_window',
                'target': 'new',
            }
        else:
            return {}
