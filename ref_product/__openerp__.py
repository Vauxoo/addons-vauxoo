# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: jorge_nr (jorge_nr@vauxoo.com)
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
{
    "name" : "Ref Product",
    "version" : "0.1",
    "author" : "Vauxoo",
    "category" : "Generic Modules/Others",
    "description" : """
When you install this module, the form view of the products
accommodates the fields to give better presentation of the information
presented to the end user.

    Fields are accommodated are:

        *Can be Purchased
        *Can be used in contracts.

    This module will be installed until the following bug remains fixed:

        https://bugs.launchpad.net/openobject-addons/+bug/1188863

    Image url:

        https://www.diigo.com/item/image/3z3vg/kj84
    """,
    "website" : "http://www.vauxoo.com/",
    "license" : "AGPL-3",
    "depends" : [
                    'base',
                    'hr_expense',
                ],
    "update_xml" : [],
    'data' : [
                'view/ref_product_view_inherit.xml',
             ],
    'installable':True,
    'auto_install':False,
}
