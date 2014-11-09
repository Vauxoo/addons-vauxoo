# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
# Credits######################################################################
#    Coded by: Humberto Arocha <hbto@vauxoo.com>
#    Planified by: Humberto Arocha <hbto@vauxoo.com>
#    Audited by: Vauxoo C.A.
###############################################################################
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
#
###############################################################################
{
    "name": "Product Category Name Untranslated",
    "version": "0.1",
    "author": "Vauxoo",
    "category": "Generic Modules",
    "description": """
Product Category Name Untranslated
==================================

This module takes away the translation attribute from field `name` on model
    product.category as sometimes results annoying to end user when duplicating
    product categories or when changing name and no aware of the other
    languages.

WARNING
=======
    After installing this module you should execute the following script in
    order to preserve your secondary language strings, i.e., Your secondary
    language is the one to be shown in the Product Category Names

    UPDATE product_category
    SET name = subview.new_name
    FROM (
    SELECT pc.id AS ctg_id, pc.name AS old_name, it.value AS new_name
    FROM product_category pc
    INNER JOIN ir_translation it ON (pc.id = it.res_id)
    WHERE it.name = 'product.category,name'
    AND it.value <> pc.name
    ) subview
    WHERE subview.ctg_id = id;
""",
    "website": "http://vauxoo.com",
    "license": "",
    "depends": [
        "product",
    ],
    "demo": [
    ],
    "data": [
    ],
    "test": [],
    "js": [],
    "css": [
    ],
    "qweb": [],
    "installable": True,
    "auto_install": False,
    "active": False
}
