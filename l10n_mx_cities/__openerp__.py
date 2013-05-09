# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: moylop260 (moylop260@vauxoo.com)
#              Isaac Lopez (isaac@vauxoo.com)
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

{
    "name" : "Mexican Cities",
    "version" : "1.0",
    "author" : "Vauxoo",
    "category" : "Localization/Mexico",
    "description" : """This module adds all Mexico's cities based in SEPOMEX
    You can download the xml file from http://www.correosdemexico.gob.mx/ServiciosLinea/Paginas/DescargaCP.aspx, save it in source folder with the name 'l10n_mx_cities.xml'
    and execute read_write_xml.py file for generate a xml compatible with OpenERP in the folder "data".
    When you install this module, OpenERP is going to import the cities from the xml file "data/l10n_mx_cities.xml"
    """,
    "website" : "http://www.vauxoo.com/",
    "license" : "AGPL-3",
    "depends" : [
        "base",
        "city",
        "l10n_mx_states",
    ],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
        "data/l10n_mx_cities.xml",
    ],
    "installable" : True,
    "active" : False,
}



