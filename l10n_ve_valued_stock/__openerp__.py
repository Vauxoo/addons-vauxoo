#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
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
################################################################################

{
    "name" : "Valued Stock",
    "version" : "0.2",
    "author" : "OpenERP Venezuela",
    "category" : "General",
    "website": "http://wiki.openerp.org.ve/",
    "description": '''
                    Permite obtener el valor del costo al momento de generar el movimiento de inventario por cada linea del mismo.
                   ''',
    "depends" : [   "stock",
                    "product_historical_price",
                ],
    "init_xml" : [],
    "update_xml" : [
            "stock_view.xml",
    ],
    "active": False,
    "installable": True
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:





