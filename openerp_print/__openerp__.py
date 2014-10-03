# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
###############Credits######################################################
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
    "name": "Print Models and Reports", 
    "version": "0.2", 
    "author": "Vauxoo", 
    "category": "Generic Modules/MRP/Accounting", 
    "description": """
        Impresion de Reportes
        Configuraciones Previas:
        1-  Instalar pycups:    # aptitude install python-cups
        2-                      # apt-get install system-config-printer
        3-  Acceder al archivo de configuracion de cups (/etc/cups/cupsd.conf) y modificar:
            - En la Seccion: Only listen for connections from the local machine.
                Listen 631
                Listen /var/run/cups/cups.sock
            - En la Seccion: Default authentication type, when authentication is required...
                DefaultAuthTypeDigest
                DefaultEncryptionRequired
                DefaultEncryption Never
            - En la Seccion: Restrict access to the server...
                <Location />
                  Allow all
                </Location>
            - En la Seccion: Restrict access to the admin pages...
                <Location /admin>
                  Allow all
                </Location>
            - En la Seccion: Restrict access to configuration files...
                <Location /admin/conf>
                  AuthType Default
                  Require user @SYSTEM
                  Order allow,deny
                </Location>
        4-  Reiniciar cups:    #  /etc/init.d/cups restart
        5-  Instalar:   # aptitude install lpr #NO INSTALAR (por ahora)
        6-  Istalar:    # aptitude install cups cups-driver-gutenprint gutenprint-locales foomatic-db foomatic-db-gutenprint foomatic-db-engine foomatic-filters foomatic-db-hpijs cups-bsd foo2zjs
        7-  PROCESO DE AÑADIR LA IMPRESORA
            7.1- Acceder a Common UNIX Printing System (asistente de impresoras Web): http://localhost:631/ si es, desde una maquina virtual con: http://192.168.*.*
            7.2- Anadir la Impresora que se desea administrar
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