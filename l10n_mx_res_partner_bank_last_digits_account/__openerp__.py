# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: Luis Torres (luis@vauxoo.com)
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
    "name" : "Tomar los 4 ultimos digitos de la cuenta en res.partner.bank",
    "version" : "1.0",
    "author" : "Vauxoo",
    "category" : "Localization/Mexico",
    "description" : """Take the last 4 digits of the account in res.partner.bank
    """,
    "website" : "www.vauxoo.com",
    "license" : "AGPL-3",
    "depends" : ["base",],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : ['last_digits_view.xml'],
    "installable" : True,
    "active" : False,
}
