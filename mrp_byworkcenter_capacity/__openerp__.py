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

This module adds two features to the mrp module. First, create a new model
named ``Scheduled Work Orders`` that represent the estimated work orders to be
done. When a manufacturing order is confirmed then the 'estimated' work orders
are created. Later, using the mrp_consume_produce module you can consume and
produce real work orders (in development).

This module also adds the feature of taking into account the workcenters
maximum capacity by product for the process of automatic generating the work
orders of a manufacturing order to make batch orders.

Instead of generate one workorder by every activity loaded in
the manufacturing order routing (the basic process) it create so many
work orders needed to the production capacity in the workcenters. There is two
criterias for the workcenters capacitys:

- **Avoid Production Bottleneck:** Will create the batch work orders taking into a
  count the minium workcenter capacity.
- **Maximize Production Cost:** For every workcenter will create a batch of works
  orders that always explotes the product capacity of the workcenter.

This criteria needs to be set, by default it use the
*Avoid Production Bottleneck* option. For change this option have this
alternatives:

- Go to ``Settings > Companies > (Select Companie) > Configuration (Tab) >
  Logistics > Production Batch Process Type``.
- Go to ``Settings > Configuration > Manufacturing > Manufacturing Order >
  Planning > Production Batch Process Type``

For example. If I want to produce 100 pounds of meat but my related workcenters
process only 20 pounds at time, this feature will create 5 work orders each to
process 20 pounds of the production order 100 pounds.

This is helpfull because in real life does not happen that all the process
of a big capacity manufacturing order is process at once.
""",
    "depends": ["mrp", "mrp_operations", "mrp_consume_produce"],
    "data": [
        'view/mrp_byworkcenter_capacity_view.xml',
        'view/res_config_view.xml',
        'view/res_company_view.xml',
    ],
    "demo": [],
    "test": [],
    "active": False,
    "installable": True,
}