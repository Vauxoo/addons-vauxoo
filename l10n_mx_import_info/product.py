# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    Nhomar Hernandez nhomar@vauxoo.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import pooler, tools


class product_import_info(osv.Model):
    _name = 'product.import.info'
    _rec_name = 'import_id'

    def _get_qtymoved(self, cr, uid, ids, field_name, arg, context=None):
    # TODO ISAAC: Metodo para calcular el la cantidad de movimientos ya imputados a esta import info. Analizar desde cero, no contemplar lo que este escrito aqui.
    # Recordar quitar los TODO.
        if context is None:
            context = {}
        '''
        cr.execute("""
            SELECT stock_move.id, stock_move.product_qty, stock_picking.type,
                stock_move.*
            FROM stock_move
            INNER JOIN stock_tracking
               ON stock_tracking.id = stock_move.tracking_id
            INNER JOIN import_info
               ON import_info.id = stock_tracking.import_id
            LEFT OUTER JOIN stock_picking
              ON stock_picking.id = stock_move.picking_id
            WHERE stock_picking.type = 'in'
              --AND stock_move.state = 'done'
        """)
        '''
        result = {}
        # print arg
        obj = self.pool.get('stock.report.tracklots')
        for i in ids:
            result[i] = 10.00
        #~ result = 5
        #~ print 'dentro del campo function, validación de _get_qtymoved el result retornado es',result

        return result

    _columns = {
        'product_id': fields.many2one('product.product', 'Product', required=True,
            domain=['|', ('type', '=', 'consu'), ('type', '=', 'product'),
            '&', ('pack_control', '=', True), ('purchase_ok', '=', True),],
            help="Product to be counted on this Import Document information"),
        'import_id': fields.many2one('import.info', 'Import Info', required=True,
            help="Import Document related"),
        'qty': fields.float('Quantity', (16, 4),
                            help="Quantity of this product on this document,"),
        'uom_id': fields.many2one('product.uom', 'UoM', required=False,
            help="Unit of measure, be care this unit must be on the same category of unit indicated on the product form,"),
        'qty_moved': fields.function(_get_qtymoved, method=True, type='float',
            string='Qty already moved',),
#       'logistical': fields.function(_calc_stock, method=True, type='text', string='Logistic',),
    }

    def _check_uom(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        for import_info in self.browse(cr, uid, ids, context=context):
            if import_info.uom_id and import_info.uom_id.category_id.id != \
                import_info.product_id.uom_po_id.category_id.id:
                return False
        return True

    _constraints = [
        (_check_uom, 'Error: The default UOM and the Import Product Info must be in the same category.', [
         'uom_id']),
    ]

    def onchange_product_id(self, cr, uid, ids, product_id, context=None):
        """
        Return a dict that contains new values, and context

        @param cr: cursor to database
        @param user: id of current user
        @param product_id: latest value from user input for field product_id
        @param args: other arguments
        @param context: context arguments, like lang, time zone

        @return: return a dict that contains new values, and context
        """
        if context is None:
            context = {}
        res = {}
        if product_id:
            res = {'value': {'uom_id': self.pool.get('product.product').browse(
                cr, uid, product_id, context).uom_po_id.id}}
        return res


class product_product(osv.Model):
    """
    product_product
    """
    _inherit = 'product.product'

    def _has_import(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        result = {}
        for i in ids:
            if len(self.browse(cr, uid, [i], context)[0].import_info_ids) != 0:
                result[i] = True
            else:
                result[i] = False
        return result
    _columns = {
        'pack_control': fields.boolean('Pack Control', required=False,
            help="If you want to track import information to be used on invoices and other documents check this field, remember, if the product is a service this information can not be tracked, if this field is checked you will need to use consumable or stockable type of product on information page."),
        'import_info_ids': fields.one2many('product.import.info', 'product_id',
            'Import Info', required=False),
        'has_import': fields.function(_has_import, method=True, type='boolean',
            string='Has Import'),
    }
