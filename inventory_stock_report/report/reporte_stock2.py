#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: Vauxoo C.A.
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

import time
from openerp.report import report_sxw


class rep_conteo_stock2(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(rep_conteo_stock2, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'get_data': self.get_data,
            'get_tipo': self.get_tipo,
            'get_category': self.get_category,
            'get_state': self.get_state,
            'get_destinado': self.get_destinado,
            'get_suministro': self.get_suministro,
            'get_qty_available': self.get_qty_available,
            'get_stock_mayor_cero': self.get_stock_mayor_cero,
            'get_code': self.get_code,
        })

    def get_tipo(self, stock=None):
        product = self.pool.get('product.template')
        cabeza = []
        boole = False
        if stock.tipo == "almacenable" or stock.tipo == "consumible":
            cabeza.append("Almacenable/Consumible")
            boole = True
        if stock.tipo == "servicio":
            cabeza.append("Servicio")
            boole = True
        if boole == False:
            cabeza.append("Almacenable - Consumible / Servicio")
        return cabeza

    def get_category(self, stock=None):
        product = self.pool.get('product.template')
        cabeza = []
        if stock.categoria:
            cabeza.append(" %s" % (stock.categoria.name))
        else:
            cabeza.append("Todas las Categorias")
        return cabeza

    def get_state(self, stock=None):
        product = self.pool.get('product.template')
        cabeza = []
        if stock.estado:
            cabeza.append(" %s" % (stock.estado))
        else:
            cabeza.append("Todas los Estados")
        return cabeza

    def get_stock_mayor_cero(self, stock=None):
        return stock.stockmayorcero

    def get_destinado(self, stock=None):
        product = self.pool.get('product.template')
        cabeza = " "

        if stock.vendible:
            cabeza = "Vendible "

        if stock.comprable:
            cabeza = cabeza+" Comprable"

        if stock.alquilable:
            cabeza = cabeza + "Alquilable"

        if not stock.vendible and not stock.comprable and not stock.alquilable:
            cabeza = "Vendible Comprable Alquilable"
        return cabeza

    def get_suministro(self, stock=None):
        product = self.pool.get('product.template')
        cabeza = []
        if stock.suministro:
            cabeza.append(" %s" % (stock.suministro))
        else:
            cabeza.append("Todas los Tipos de Suministro")
        return cabeza

    def get_data(self, stock=None):
        product = self.pool.get('product.template')
        merge = []
        # para el tipo del producto####################

        if stock.tipo == "almacenable":
            merge.append(('type', '=', "product"))
        if stock.tipo == "consumible":
            merge.append(('type', '=', "consut"))
        if stock.tipo == "servicio":
            merge.append(('type', '=', "service"))

        # para la categoria####################

        if stock.categoria:
            merge.append(('categ_id', '=', stock.categoria.id))

        # para el estado####################
        if stock.estado:
            if stock.estado == "desarrollo":
                merge.append(('state', '=', "draft"))

            if stock.estado == "produccion":
                merge.append(('state', '=', "sellable"))

            if stock.estado == "fin":
                merge.append(('state', '=', "end"))

            if stock.estado == "obsoleto":
                merge.append(('state', '=', "obsolete"))

            if stock.estado == "none":
                merge.append(('state', '=', None))

        # destinado a ser: vendible, conyable, alquilable####################
        if stock.vendible:
            merge.append(('sale_ok', '=', True))

        if stock.comprable:
            merge.append(('purchase_ok', '=', True))

        if stock.alquilable:
            merge.append(('rental', '=', True))

        # tipo de suministro####################

        if stock.suministro == "comprar":
            merge.append(('supply_method', '=', 'produce'))

        if stock.suministro == "producir":
            merge.append(('supply_method', '=', 'buy'))

        id_productos = product.search(self.cr, self.uid, merge, order="name")
        data = product.browse(
            self.cr, self.uid, id_productos)  # lista de product_template que cumplen la condicion
        return data

    def get_qty_available(self, id_template):
        qty = 0.0
        qty2 = 0.0
        product = self.pool.get('product.product')
        try:
            id_producto = product.search(self.cr, self.uid, [
                                         ('product_tmpl_id', '=', id_template.id)])
            producto = product.browse(self.cr, self.uid, id_producto[0])
            qty = producto.qty_available
            qty2 = producto.virtual_available
            res = [qty, qty2]
            return res
        except:
            res = [qty, qty2]
            return res

    def get_code(self, id_template):
        code = "-"
        product = self.pool.get('product.product')
        try:
            id_producto = product.search(self.cr, self.uid, [
                                         ('product_tmpl_id', '=', id_template.id)])
            producto = product.browse(self.cr, self.uid, id_producto[0])
            code = producto.code
            return code
        except:
            return code


report_sxw.report_sxw(
    'report.hoja222',
    'stock.total',
    'addons/inventory_stock_report/report/hoja_conteo_qty2.rml',
    parser=rep_conteo_stock2,
)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
