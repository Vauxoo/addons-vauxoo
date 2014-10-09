#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Humberto Arocha <hbto@vauxoo.com>
#    Planified by: Rafael Silva <rsilvam@vauxoo.com>
#    Audited by: Nhomar Hernandez <nhomar@vauxoo.com>
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
    "name" : "Sale of Uncommitted Products",
    "version" : "0.1",
    "author" : "Vauxoo",
    "category" : "Generic Modules",
    "website": "http://www.vauxoo.com",
    "description": '''
This module:
*) Adds a new state to the sale order model, committed
*) Adds a new activity to the sale order workflow, commit
*) Adds two new transitions from draft to commit,
    -) One which could force commitment of sale order,
    -) The other will check if any product does not overflow the availability
*) Modifies the existing Transition from draft to router
and changes it from commit to router.

*) Adds a wizard so that it is possible to assign groups to the newly transitions.
*) Adds two fields to the product.product model:
    -) qty_committed: amounts the quantity of products in sale orders with state committed
    -) qty_uncommitted: amounts the quantity of available to commit
    this amount is, qty_available + outgoing - qty_committed
''',
    "depends" : [
                "base",
                "sale",
                "product",
                "stock",
                ],
    "init_xml" : [],
    "demo_xml" : [

    ],
    "update_xml" : [
        'view/product_view.xml',
        'view/sale_view.xml',
        'view/sale_double_validation_installer.xml',
        'workflow/sale_workflow.xml',
        'security/groups.xml',
    ],
    "active": False,
    "installable": True
}
