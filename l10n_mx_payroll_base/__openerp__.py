#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: vauxoo consultores (info@vauxoo.com)
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
    "name": "Mexican Payroll",
    "version": "1.0",
    "depends": [
                "base",
                "account",
                "hr_payroll",
                "l10n_mx_states",
                "l10n_mx_regimen_fiscal",
                "l10n_mx_hr_payroll",
                "l10n_mx_data_bank",
                "l10n_mx_partner_address",
                "l10n_mx_payroll_concept",
                "l10n_mx_payroll_regime_employee",
                "l10n_mx_payroll_risk_rank_contract",
                "l10n_mx_payment_method",
                "l10n_mx_facturae_cer",
                "l10n_mx_ir_attachment_facturae",
                "l10n_mx_params_pac",
                "l10n_mx_facturae_groups",
                "hr_payroll_account",
    ],
    "author": "Vauxoo",
    "description": """
Mexican Payroll
===============

This module installs the necessary work to CFDI MX Payroll. 
For example, data banks, catalogs required for SAT to generate payroll, 
fields needed in view of employees and contracts.


ftp://ftp2.sat.gob.mx/asistencia_servicio_ftp/publicaciones/cfdi/catalogoscomplementonomina.pdf


ftp://ftp2.sat.gob.mx/asistencia_servicio_ftp/publicaciones/cfd/nomina11.pdf


ftp://ftp2.sat.gob.mx/asistencia_servicio_ftp/publicaciones/cfdi/guianomina.pdf
    """,
    "website": "http://vauxoo.com",
    "category": "Addons Vauxoo",
    "data": [
        "view/l10n_mx_payroll_base_view.xml",
        "view/ir_attachment_facturae_view.xml",
        'security/ir.model.access.csv',
    ],
    "demo" : [
        "demo/l10n_mx_payroll_partner.xml",
        "demo/account_payroll_demo.xml",
        "demo/payroll_concept_account_demo.xml",
        "demo/l10n_mx_payroll_demo.xml",
        "demo/l10n_mx_payroll_contract.xml",
        "demo/l10n_mx_payroll_cfdi0.xml",
        "demo/l10n_mx_payroll_partner.xml",
        "demo/l10n_mx_payroll_users.xml",
    ],
    "test": [
    ],
    "active": False,
    "installable": True,
}
