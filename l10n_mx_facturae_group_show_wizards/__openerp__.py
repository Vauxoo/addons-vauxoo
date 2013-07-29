#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Luis Ernesto García (ernesto_gm@vauxoo.com)
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
    "name" : "Group For Wizards Of Facturae",
    "version" : "1.0",
    "author" : "Vauxoo",
    "category" : "Localization/Mexico",
    "description" : """
Group for show wizards of FacturaE
==================================

This module creates the group Show Default Wizards FacturaE, if a user has this group,\n 
can see the facturae wizards, however is advisable that nobody has this group assigned. \n
Wizards to show:\n

- Factura Electronica XML \n
- Cancelar FActura PAC SF \n
- Subir Factura al PAC V6 \n
    """,
    "website" : "http://www.vauxoo.com/",
    "license" : "AGPL-3",
    "depends" : ["base",
    ],
    "demo" : [],
    "data" : [
        "security/res_groups.xml",
    ],
    "installable" : True,
    "active" : False,
}
