# -*- encoding: utf-8 -*-
#
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2014 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#
#    Coded by: Luis Torres (luis_t@vauxoo.com)
#
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
#

{
    "name": "Validate XML SAT",
    "version": "1.0",
    "author": "Vauxoo",
    "category": "Localization/Mexico",
    "description" : """
    This module add an wizard to validate if an XML already was validated in the SAT

    Added
    sudo apt-get install python-soappy
    sudo pip install pillow qrcode
    wget http://security.ubuntu.com/ubuntu/pool/main/s/suds/python-suds_0.4.1-2ubuntu1_all.deb
    sudo dpkg -i python-suds_0.4.1-2ubuntu1_all.deb

    """,
    "website": "http://www.vauxoo.com/",
    "license": "AGPL-3",
    "depends": [
        "l10n_mx_facturae_base",
    ],
    "demo": [
        "demo/attachment_validate_sat_demo.xml"
    ],
    "test": [
        "test/xml_validate_sat.yml",
    ],
    "data": [
        "view/wizard_validate_uuid_xml_view.xml",
    ],
    "installable": True,
    "active": False,
}
