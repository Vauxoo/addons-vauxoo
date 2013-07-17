# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Fernando Irene Garcia (fernando@vauxoo.com)
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
    "name" : "Invoice Workflow Security",
    "version" : "0.1",
    "author" : "Vauxoo",
    "category" : "Localization/Mexico",
    "license" : "AGPL-3",
    "description": """ Este modulo genera por medio de data xml 2 grupos:
                        1) invoice_cancel
                        2) invoice_reset_draft
                       Asignados a los botones cancel y set_to_draft respectivamente. """,
    "depends" : ["base", "account", "l10n_mx_facturae_groups",],
    "demo" : [],
    "data" : ['security/invoice_wkf_security_data.xml', 
        'invoice_wkf_security_view.xml'],
    "active": False,
    "installable": True,
}
