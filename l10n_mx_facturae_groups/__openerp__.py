#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Vauxoo (<http://vauxoo.com>).
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

{
    "name" : "Crea la aplicación para los grupos de la Factura Electronica",
    "version" : "1.0",
    "author" : "Vauxoo",
    "category" : "Localization/Mexico",
    "description" : """Create the application with the groups: User y Manager.
                    This application is for Electronic Invoice of México
    """,
    "website" : "http://vauxoo.com",
    "license" : "AGPL-3",
    "depends" : ["base", "document"
        ],
    "demo" : [],
    "test": [],
    "data" : ["security/l10n_mx_facturae_security_groups.xml",
            ],
    "images": [],
    'application': False,
    "active" : False,
    "installable" : True,
}
