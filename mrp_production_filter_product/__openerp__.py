#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Juan Carlos Funes(juan@vauxoo.com)
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
    "name" : "Inherit filter_domain product_id field in search view of mrp_production",
    "version" : "1.0",
    "depends" : ['mrp'],
    "author" : "Vauxoo",
    #"license" : "AGPL-3",
    "description" : """This module inherit filter_domain product_id field in search view of mrp_production
    """,
    "website" : "http://vauxoo.com",
    "category" : "Generic Modules",
    "init_xml" : [],
    "demo_xml" : [],
    "test": [],
    "update_xml" : ['mrp_production_view.xml',
    ],
    "active": False,
    "installable": True,
}

