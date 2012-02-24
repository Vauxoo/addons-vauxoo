# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info moylop260 (moylop260@vauxoo.com)
############################################################################
#    Coded by: moylop260 (moylop260@vauxoo.com)
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
    'name': 'l10n_mx_facturae_email - Use to Send Customers the selected electronic invoice attachment by Email',
    'version': '0.1',
    "author" : "Vauxoo",
    "category" : "Localization/Mexico",
    'description': """Use Email client module to send to customers
the selected electronic invoice attachment by Email.
""",
    "website" : "http://www.vauxoo.com",
    "license" : "AGPL-3",
    "depends" : ["email_template", "l10n_mx_facturae"],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
        #"email_facturae_mx_wizard.xml",
        "wizard/email_template_send_wizard_view.xml",
        "l10n_mx_facturae_email_demo.xml",
    ],
    "installable" : True,
    "active" : False,
}
