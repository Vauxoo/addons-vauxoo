#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: María Gabriela Quilarque  <gabriela@vauxoo.com>
#              Luis Escobar              <luis@vauxoo.com>
#    Planified by: Nhomar Hernandez <nhomar@vauxoo.com>
#    Finance by: Vauxoo, C.A. http://vauxoo.com
#    Audited by: Humberto Arocha <humberto@vauxoo.com>
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
	"name" : "Vauxoo Report Multicompany",
	"version" : "0.7",
	"author" : "Vauxoo",
	"category" : "Generic Modules/Others",
	"website": "http://vauxoo.com/",
	"description": '''
	               Agrega un tab en la Compañia que va a contener los reportes personalizados.
                    ''',
	"depends" : ["base", "account", ],
	"data" : [
                "security/ir.model.access.csv",
		        "report_multicompany_view.xml",
	],
	"active": False,
	"installable": True,
}
