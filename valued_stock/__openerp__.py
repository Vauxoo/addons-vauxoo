#!/usr/bin/python
# -*- encoding: utf-8 -*-
##############################################################################
#
#    Stock Valued module for OpenERP, Module to manage cost
#    Copyright (C) 2013 Vauxoo (<http://vauxoo.com>) author
#
#    This file is a part of Stock Valued
#
# Credits######################################################
#    Coded by: Vauxoo C.A.
#    Planified by: Nhomar Hernandez
#    Audited by: Vauxoo C.A.
#
#    Stock Valued is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Stock Valued is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    "name": "Valued Stock",
    "version": "0.2",
    "author": "Vauxoo",
    "category": "General",
    "website": "http://www.vauxoo.com",
    "description": '''
Permite obtener el valor del costo al momento de generar el movimiento de
inventario por cada linea del mismo.
                   ''',
    "depends": ["stock",
                "product_historical_price",
                ],
    "init_xml": [],
    "update_xml": [
            "stock_view.xml",
    ],
    "active": False,
    "installable": False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
