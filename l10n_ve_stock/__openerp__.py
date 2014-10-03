#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: javier@vauxoo.com
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
    "name": "Formatos Nota de Entrega y Guia Despacho", 
    "version": "0.3", 
    "author": "Vauxoo", 
    "category": "Localization", 
    "description": """
    Notas de entrega
    Guías de despacho según decreto 
    0591
    Referencia Legal:
    http://wiki.openerp.org.ve/index.php?title=0591
""", 
    "website": "http://vauxoo.com", 
    "license": "GPL-3", 
    "depends": [
        "stock_valued"
    ], 
    "demo": [], 
    "data": [
        "stock_valued_sequence.xml", 
        "wizard/wiz_picking_valued.xml", 
        "stock_valued_view.xml", 
        "stock_valued_report.xml"
    ], 
    "test": [], 
    "js": [], 
    "css": [], 
    "qweb": [], 
    "installable": False, 
    "auto_install": False
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: