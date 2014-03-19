# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Luis Ernesto Garcia Medina (ernesto_gm@vauxoo.com)
#
############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
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
    "name": "Regime of payrolls",
    "version": "1.0",
    "author": "Vauxoo",
    "category": "Generic Modules",
    "description" : """
Regime of payrolls
==================
    
    Add model and data regime of employee requested by the SAT based upon the payrolls
    
    ftp://ftp2.sat.gob.mx/asistencia_servicio_ftp/publicaciones/cfdi/catalogoscomplementonomina.pdf

    """,
    "website": "http://www.vauxoo.com/",
    "license": "AGPL-3",
    "depends": ["base", "hr_payroll",
                ],
    "data": [
        "data/payroll_regime_data.xml",
        "view/payroll_regime_employee_view.xml",
        "view/hr_employee_payroll_regime_view.xml",
        'security/ir.model.access.csv',
    ],
    "installable": True,
    "active": False,
}
