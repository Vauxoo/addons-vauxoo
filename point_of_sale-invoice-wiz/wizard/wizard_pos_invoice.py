# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: el_rodo_1 (rodo@vauxoo.com)
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

import time

from osv import osv, fields
from tools.translate import _


class wizard_pos_invoice(osv.osv_memory):
    _name = 'wizard.pos.invoice'

    _columns = {
        'group': fields.boolean(string='Agrupar Por Cliente'),
        'pos_ids': fields.many2many('pos.order','pos_res_partner_rel','pos_id','invoice_id',string='Ordenes',domain=[('state','=','paid')]),
        'partner_id': fields.many2one('res.partner',string='Reasignar Cliente'),
    }
    
    _defaults = {
        'group': True,
    }

    def default_get(self, cr, uid, fields, context=None):
        res = super(wizard_pos_invoice, self).default_get(cr, uid, fields, context=context)
        pos_obj=self.pool.get('pos.order')
        if context is None:
            context = {}
        new_ids=pos_obj.search(cr,uid,[('id', 'in', tuple(context['active_ids'])),('state', '=', 'paid')],context=context) 
        res.update({'pos_ids':new_ids})
        return res

        
    def create_invoice(self, cr, uid, ids, context=None):
        datas = {}
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        if data['group']:
            context.update({'group': True})
        pos_obj=self.pool.get('pos.order')
        new_ids=pos_obj.search(cr,uid,[('id', 'in', tuple(context['active_ids'])),('state', '=', 'paid')],context=context) 
        if data['partner_id']:
            pos_obj.write(cr, uid, new_ids,{'partner_id':data['partner_id'][0]}, context=context)
        pos_obj.action_invoice(cr, uid, new_ids, context=context)
        return {}


wizard_pos_invoice()
