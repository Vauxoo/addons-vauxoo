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

from openerp.osv import osv, fields
from openerp.tools.translate import _


class wizard_report_process(osv.TransientModel):
    _name = 'wizard.report.process'

    _columns = {
        'product_ids': fields.many2many('product.product', 'temp_product_rel',
                                        'temp_id', 'product_id', 'Productos'),
        'print': fields.selection([('sin', 'Sin Agrupar'),
                                   ('agrupado', 'Agrupado'),
                                   ('ambos', 'Ambos')], 'Imprimir',
                                  required=True),
    }

    _defaults = {
        'print': 'ambos'
    }

    def default_get(self, cr, uid, fields, context=None):
        """ To get default values for the object.
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param fields: List of fields for which we want default values
         @param context: A standard dictionary
         @return: A dictionary which of fields with values.
        """
        if context is None:
            context = {}
        prod_obj = self.pool.get('product.product')
        production_obj = self.pool.get('mrp.production')
        res = super(wizard_report_process, self).default_get(
            cr, uid, fields, context=context)
        production_ids = context.get('active_ids', [])
        if not production_ids:
            return res
        prod_list = []
        for production in production_obj.browse(cr, uid, production_ids):
            for line in production.move_lines:
                prod_list.append(line.product_id.id)
        res['product_ids'] = prod_list
        return res

    def check_report(self, cr, uid, ids, context=None):
        datas = {}
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]

        datas = {
            'ids': context.get('active_ids', []),
            'model': 'wizard.report.process',
            'form': data,
            'uid': uid,
        }

        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'process.report',
            'datas': datas,
        }
