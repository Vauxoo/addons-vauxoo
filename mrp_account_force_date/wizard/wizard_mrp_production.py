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

class wizard_mrp_production(osv.TransientModel):
    _name='wizard.mrp.production'
    _columns={
        'new_date' : fields.datetime('New Date', required=True),
        'mrp_ids': fields.many2many('mrp.production',
          'mrp_production_rel', 'temp_id', 'mrp_id', 'Mrp Productions'),
    }
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None:context = {}
        mrp_ids = context['active_ids']
        res = super(wizard_mrp_production, self).default_get(cr, uid, 
            fields, context=context)
        res.update({
            'mrp_ids': mrp_ids or False,
        })
        return res

    def wizard_mrp_change_date(self, cr, uid, ids, context=None):
        """ Calls the function mrp_change_date to change the date.
        @return: {}
        """
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, [])
        mrp_ids = data[0]['mrp_ids']
        new_date = data[0]['new_date'] or False
        self.pool.get('mrp.production').mrp_change_date(cr, uid,
            mrp_ids, new_date, context=context)
        return {}
