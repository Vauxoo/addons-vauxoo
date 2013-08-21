#!/usr/bin/python
# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
############# Credits #########################################################
#    Coded by: Katherine Zaoral          <kathy@vauxoo.com>
#    Planified by: Katherine Zaoral      <kathy@vauxoo.com>
#    Audited by: Humberto Arocha         <hbto@vauxoo.com>
###############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################

{
    "name": "MRP Work Center Capacity",
    "version": "1.0",
    "author": "Vauxoo C.A.",
    "website": "http://www.openerp.com.ve",
    "category": "MRP",
    "description": """
MRP Work Center Capacity
========================

This module add the feuture of take in count the workcenters minimum and
maximum when automatic generating the work orders for a production order.
Instead of generate one work order by every activity loaded in the production
order routing (the basic process) it create so many work orders needed to the
production capacity in every work center.
 
For example. If I want to produce 100 pounds of meat but my related work center
process only 20 pounds at time, this feature will create 5 work orders each to
process 20 pounds of the production order 100 pounds.

This is helpfull because in real life does not happend that all the process
of a big capacity production order is process at once.

""",
    "depends": ["mrp", "mrp_operations", "mrp_consume_produce"],
    "data": [
        'view/mrp_byworkcenter_capacity_view.xml',
    ],
    "demo": [],
    "test": [],
    "active": False,
    "installable": True,
}