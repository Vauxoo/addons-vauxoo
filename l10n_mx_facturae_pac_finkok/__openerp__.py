# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: moylop260 (moylop260@vauxoo.com)
#              Isaac Lopez (isaac@vauxoo.com)
#              Carlos Hdz (juan@vauxoo.com)
#              Luis Garcia (ernesto_gm@vauxoo.com)
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
    "name" : "Creacion de Factura Electronica para Mexico (CFDI-2014) - PAC Finkok",
    "version" : "1.0",
    "author" : "Vauxoo",
    "category" : "Localization/Mexico",
    "description" : """This module creates interface for e-invoice files from invoices with Solucion Factible.
Ubuntu Package Depends:
    sudo apt-get install python-soappy 
    sudo pip install pillow qrcode
    wget http://security.ubuntu.com/ubuntu/pool/main/s/suds/python-suds_0.4.1-2ubuntu1_all.deb
    dpkg -i python-suds_0.4.1-2ubuntu1_all.deb
""",
    "website" : "http://www.vauxoo.com/",
    "license" : "AGPL-3",
    "depends" : ["l10n_mx_facturae_groups", "l10n_mx_params_pac", 
        "l10n_mx_account_tax_category",
        "l10n_mx_facturae_report",
        "l10n_mx_facturae_seq", 
        "l10n_mx_ir_attachment_facturae",
        "l10n_mx_facturae_base",
        "l10n_mx_facturae_group_show_wizards",
        "l10n_mx_settings_facturae",
        ],
    "demo" : [
        "demo/l10n_mx_facturae_pac_finkok_demo.xml",
        "demo/l10n_mx_facturae_seq_demo.xml",
        "demo/l10n_mx_payroll_seq_demo.xml",
        "demo/l10n_mx_facturae_seq_demo_customer_refund.xml",
    ],
    "data" : [
    ],
    "test" : [],
    "installable" : True,
    "active" : False,
}
