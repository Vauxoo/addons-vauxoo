# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
# Credits ###################################################
#    Coded by: nhomar@vauxoo.com,
#    Planified by: Nhomar Hernandez
#    Finance by: Helados Gilda, C.A. http://heladosgilda.com.ve
#    Audited by: Humberto Arocha humberto@vauxoo.com
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##############################################################################
{
    "name": "Configure printers to send Directly to them",
    "summary": """You can set a printer using cups and force reports go to that
    printer""",
    "version": "0.3",
    "author": "Vauxoo",
    "category": "Tools",
    "description": """

This module needs to be migrated to v8.0
========================================

Any contribution/comment is welcome until now no customer requires
migration.

Print reports directly to printers

Configuring your server:
------------------------

- Install pycups:    # aptitude install python-cups
-                      # apt-get install system-config-printer
- Edit the cups's config file (/etc/cups/cupsd.conf) y modificar:
    - In Section: Only listen for connections from the local machine.
        Listen 631
        Listen /var/run/cups/cups.sock
    - In Section: Default authentication type, when authentication is required...
        DefaultAuthTypeDigest
        DefaultEncryptionRequired
        DefaultEncryption Never
    - In Section: Restrict access to the server...
        <Location />
            Allow all
        </Location>
    - In Section: Restrict access to the admin pages...
        <Location /admin>
            Allow all
        </Location>
    - In Section: Restrict access to configuration files...
        <Location /admin/conf>
            AuthType Default
            Require user @SYSTEM
            Order allow,deny
        </Location>
-  Restart cups:    #  /etc/init.d/cups restart
-  Install:   # aptitude install lpr #NO INSTALAR (por ahora)
-  Install:    # aptitude install cups cups-driver-gutenprint gutenprint-locales foomatic-db foomatic-db-gutenprint foomatic-db-engine foomatic-filters foomatic-db-hpijs cups-bsd foo2zjs
-  Add your printer normally as any printer in cups
    - Go to (asistant web printers): http://ip.server.with.cups:631/.
    - Add the printer there.

TODO:

- Explain odoo's side, but it will be done in the rewrite to v8.0.
- Migrate to v8.0.
- autodiscover printers.

make a PR with your new features or make a bug on github.
    """,
    "website": "http://vauxoo.com",
    "license": "",
    "depends": [
        "base"
    ],
    "demo": [],
    "data": [
        "security/groups.xml",
        "security/ir.model.access.csv",
        "print_model_view.xml",
        "res_company.xml"
    ],
    "test": [],
    "js": [],
    "css": [],
    "qweb": [],
    "installable": False,
    "auto_install": False,
    "active": False
}
