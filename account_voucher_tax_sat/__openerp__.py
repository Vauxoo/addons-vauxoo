#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Julio Cesar Serna Hernandez(julio@vauxoo.com)
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
    "name": "Account Voucher Tax SAT",
    "version": "1.0",
    "author" : "Vauxoo",
    "category": "Accounting",
    "website" : "http://www.vauxoo.com/",
    "description": """ 
Polizas de SAT:
===============

1.- Crea los apuntes contables para los impuestos con retenciones
2.- Crea provicion de pago al SAT
3.- Crea apuntes contables para las retenciones de IVA
    """,
    'depends': [
        'account',
        'account_voucher_tax'
        ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'wizard/account_tax_sat_view.xml',
        'view/account_voucher_tax_sat_view.xml',
      
        ],
    'demo': [],
    'test': [],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
