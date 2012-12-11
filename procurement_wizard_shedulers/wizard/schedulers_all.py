#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Juan Carlos Funes(juan@vauxoo.com)
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
################################################################################

import threading
import pooler
import netsvc
import os

from osv import osv, fields

class procurement_compute_product(osv.osv_memory):
    _name = 'procurement.order.compute.product'
    _description = 'Compute all schedulers'

    _columns = {
        'automatic': fields.boolean('Automatic orderpoint',help='Triggers an automatic procurement for all products that have a virtual stock under 0. You should probably not use this option, we suggest using a MTO configuration on products.'),
        'product_ids': fields.many2many('product.product', 'procurement_product_rel', 'procurement_id', 'product_id', 'Products')
    }

    _defaults = {
         'automatic': lambda *a: False,
    }

    def _procure_calculation_product(self, cr, uid, ids, products, context=None):
        """
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: List of IDs selected
        @param context: A standard dictionary
        """
        proc_obj = self.pool.get('procurement.order')
        #As this function is in a new thread, i need to open a new cursor, because the old one may be closed
        new_cr = pooler.get_db(cr.dbname).cursor()
        for proc in self.browse(new_cr, uid, ids, context=context):
            proc_obj.run_scheduler2(new_cr, uid, automatic=proc.automatic, product_ids=products, use_new_cursor=new_cr.dbname,\
                    context=context)
        #close the new cursor
        new_cr.close()
        return {}

    def procure_calculation(self, cr, uid, ids, context=None):
        """
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: List of IDs selected
        @param context: A standard dictionary
        """
        form = self.read(cr,uid,ids,[])
        products = form and form[0]['product_ids'] or False
        threaded_calculation = threading.Thread(target=self._procure_calculation_product, args=(cr, uid, ids, products, context))
        threaded_calculation.start()
        return {'type': 'ir.actions.act_window_close'}

procurement_compute_product()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
