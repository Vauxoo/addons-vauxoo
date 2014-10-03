# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: julio (julio@vauxoo.com)
############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
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
# use this command
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
{
    "name": "MRP Consume Produce", 
    "version": "1.1", 
    "author": "Vauxoo", 
    "category": "Generic Modules/Production", 
    "description": """
MRP Consume Produce
===================

Add wizard to consume and produce.
It will be necesary to apply the patch patch/stock.patch located in
this module over the stock module::

    # use this command
    patch -b stock.py  stock.patch

Also is necesary to configure some permissions to use the implemented wizard.
You have to options: Go to check some options at the user:

- ``Access Rights > Other > Mrp Consume``
- ``Access Rights > Other > Mrp Consume / Manager``
- ``Access Rights > Other > MRP / Button Consume-Produce``

Or go to the ``Settings > Configuration > Manufacturing > Manufacturing Order``
and active the ``Real Consume and Produce`` option plus selecting a user type.
    """, 
    "website": "http://www.vauxoo.com/", 
    "license": "", 
    "depends": [
        "mrp", 
        "mrp_button_box"
    ], 
    "demo": [], 
    "data": [
        "wizard/wizard_view.xml", 
        "mrp_consume_produce_view.xml", 
        "security/mrp_security.xml", 
        "security/ir.model.access.csv", 
        "res_config_view.xml"
    ], 
    "test": [], 
    "js": [], 
    "css": [], 
    "qweb": [], 
    "installable": True, 
    "auto_install": False, 
    "active": False
}