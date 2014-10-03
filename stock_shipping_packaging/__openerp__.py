#!/usr/bin/python
# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
############# Credits #########################################################
#    Coded by: Yanina Aular <yanina.aular@vauxoo.com
#    Planified by: Humberto Arocha <hbto@vauxoo.com>
#    Audited by: Humberto Arocha <hbto@vauxoo.com>
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
    'name': 'Stock Shipping Packaging',
    'version': '1.0',
    'author': 'Vauxoo C.A.',
    'website': 'http://vauxoo.com',
    'category': 'Warehouse',
    'summary': 'Packaging stock moves for a delivery order',
    'description': """
========================
Stock Shipping Packaging
========================

This module allows to have best control on packaging of stock moves that belong to
a delivery order.

=============
Configuration
=============

Activate permissions:

Settings > Configuration > Warehouse > Manage multiple locations and warehouses.

Settings > Configuration > Warehouse > Allow to define several packaging methods on products.

==========
How to use
==========

In an Order Delivery can add línes of stock.moves, to each stock.move you can add a Packs
(stock.tracking) filtered by the partner of the delivery order.


""",
    'depends': ['base', 'mail', 'stock'],
    'data': [
        'view/stock_shipping_packaging_view.xml',
        ],
    'demo': [],
    'test': [],
    'active': False,
    'installable': True,
    'js': [],
    'qweb': [],
    'css': [],
    'images': [],
}
