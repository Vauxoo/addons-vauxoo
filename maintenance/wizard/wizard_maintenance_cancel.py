# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2014 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Julio Serna(julio@vauxoo.com)
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

class wizard_maintenance_cancel(osv.Model):
    _name = 'wizard.maintenance.cancel'
    
    _columns = {
        'date': fields.datetime('Compromise date', help='Use this date when you want reassign this maintenance',),
    }

    def reassign_maintenance(self, cr, uid, ids, context):
        mol_obj = self.pool.get('maintenance.order.line')
        data = self.browse(cr, uid, ids[0], context=context)
        active_ids = context.get('active_ids', [])
        if not data.date:
            raise osv.except_osv(_('Warning!'), _('You must be set a date'))
        for mol in mol_obj.browse(cr, uid, active_ids, context=context):
            mol_id = mol_obj.copy(cr, uid, mol.id, {'date_due': data.date, 'picking_ids':[], 'pendiente_id': mol.id})
            mol_obj.write(cr, uid, mol.id, {'state': 'reassigned'})
        return {
            'domain': "[('id','in', [" + str(mol_id) + "])]",
            'name': 'Mantenimientos',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'maintenance.order.line',
            'view_id': False,
            'type': 'ir.actions.act_window'
        }
        
    def cancel_maintenance(self, cr, uid, ids, context):
        active_id = context.get('active_id', [])
        self.pool.get('maintenance.order.line').write(cr, uid, active_id, {'state': 'cancel'}, context=context)
        return  {}
