#!/usr/bin/python
# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
############# Credits #########################################################
#    Coded by: Katherine Zaoral          <kathy@vauxoo.com>
#    Planified by: Katherine Zaoral      <kathy@vauxoo.com>
#    Audited by: Humberto Arocha         <hbto@vauxoo.com>
###############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################


from openerp.osv import osv, fields


class mrp_config_settings(osv.osv_memory):
    _inherit = 'mrp.config.settings'

    def _get_batch_modes(self, cr, uid, context=None):
        """
        @return: list of selection tuples for batch process type field from res
        company model.
        """
        rc_obj = self.pool.get('res.company')
        rc_fields = rc_obj.fields_get(cr, uid, ['batch_type'], context=context)
        return rc_fields['batch_type']['selection']

    def _get_current_value_batch_type(self, cr, uid, context=None):
        """
        @return the batch_type field value for the current company.
        """
        context = context or {}
        ru_obj = self.pool.get('res.users')
        return ru_obj.browse(
            cr, uid, uid, context=context).company_id.batch_type

    _columns = {
        'batch_type': fields.selection(
            _get_batch_modes,
            'Production Batch Process Type',
            help=('Two options when management the batch work orders:\n\n'
                   ' - Maxime Workcenter Productivity / Minimizing Production'
                   ' Cost: For every workcenter will'
                   ' create a batch of works orders that always explotes the'
                   ' product capacity of the workcenter.\n'
                   ' - Avoid Production Bottleneck: Will create the batch'
                   ' work orders taking into a count the minium workcenter'
                   ' capacity.')),
    }

    _defaults = {
        'batch_type': _get_current_value_batch_type
    }

    def set_batch_type(self, cr, uid, ids, context=None):
        """
        Set the production batch process type for the current company.
        @return True
        """
        context = context or {}
        rc_obj = self.pool.get('res.company')
        ru_obj = self.pool.get('res.users')
        config = self.browse(cr, uid, ids, context=context)[0]
        company_id = ru_obj.browse(cr, uid, uid, context=context).company_id.id
        rc_obj.write(
            cr, uid, [company_id], {'batch_type': config.batch_type},
            context=context)
        return True
