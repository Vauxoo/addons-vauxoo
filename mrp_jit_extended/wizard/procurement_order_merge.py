# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: fernandoL (fernando_ld@vauxoo.com)
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

class procurement_order_merge_jit_extended(osv.osv_memory):
    _name = 'procurement.order.merge.jit.extended'

    def procurement_merge_jit(self, cr, uid, ids, context=None, rec_ids=None):
        procurement_order = self.pool.get('procurement.order')
        mrp_production_pool = self.pool.get('mrp.production')
        print rec_ids,"rec ids"
        if context is None:
            context = {}
        if rec_ids is None:
            print "entre if"
            production_ids = context.get('active_ids', [])
        else:
            print "entre else"
            production_ids = rec_ids
        print production_ids, "productions ids"
        procurement_ids = []
        for production_id in production_ids:
            production_data = mrp_production_pool.browse(cr, uid, production_id, context=context)
            for line in production_data.procurement_ids:
                if line.state == 'draft':
                    procurement_ids.append(line.id)

        print procurement_ids, " procurements ids, porke no entra?"
        new_prods = procurement_order.do_merge(cr, uid, procurement_ids, context=context)
        print new_prods, "nuevas producciones ya en wizard de productions"
        if new_prods:
            self.procurement_merge_jit(cr, uid, ids, context, new_prods)
        return {}

procurement_order_merge_jit_extended()