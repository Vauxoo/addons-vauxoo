#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Jorge Angel Naranjo(jorge_nr@vauxoo.com)
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
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
{
    "name": "Wizard of Configure And Create Journal", 
    "version": "1.0", 
    "author": "Vauxoo", 
    "category": "Accounting", 
    "description": """
Configure And Create Journal:
=============================

1.- Genera wizard que te permite escoger un cuenta contable y asignar todos sus
hijos con tipo liquidez y tipo interno No conciliado.

2.- crea un diario por cada cuenta hija detectada en el paso anterior
    """, 
    "website": "http://www.vauxoo.com/", 
    "license": "", 
    "depends": [
        "account", 
        "group_configurations_account"
    ], 
    "demo": [], 
    "data": [
        "wizard/set_accounting_wizard_view.xml"
    ], 
    "test": [], 
    "js": [], 
    "css": [], 
    "qweb": [], 
    "installable": True, 
    "auto_install": False, 
    "active": False
}