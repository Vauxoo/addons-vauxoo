#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Humberto Arocha           <humberto@vauxoo.com>
#              Angelica Barrios          <angélicaisabelb@gmail.com>
#              María Gabriela Quilarque  <gabrielaquilarque97@gmail.com>
#              Javier Duran              <javier@vauxoo.com>
#    Planified by: Nhomar Hernande
#    Finance by: Helados Gilda, C.A. http://heladosgilda.com.ve
#    Audited by: Humberto Arocha humberto@vauxoo.com
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

###
### res_company --> account_management ver si se puede eliminar esta dependencia ####
### retencion_iva, base_vat_ve  ver si se puede eliminar esta dependencia

{
    "name" : "Voucher Paid support report",
    "version" : "0.2",
    "author" : "Vauxoo",
    "website" : "http://vauxoo.com",
    "category": 'Generic Modules/Accounting',
    "description": """
        Este modulo agrega al reporte del soporte de pago detallado las retenciones del Impuesto al valor agregado (IVA)

    """,
    'init_xml': [],
    "depends" : ["l10n_ve_withholding_iva", "bank_management"],
    'update_xml': [
        'bank_iva_report.xml',
    ],
    'demo_xml': [],
    'test': [],
    'installable': False,
    'active': False,
    'external_dependencies': {},
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
