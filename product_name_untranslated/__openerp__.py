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
    "name": "Product Name Untranslated",
    "version": "0.1",
    "author": "Vauxoo",
    "category": "Generic Modules",
    "description": """
Product Name Untranslated
=========================

This module takes away the translation attribute from field `name` on model
product.template as sometimes results annoying to end user when duplicating
products or when changing name and no aware of the other languages.

WARNING
=======
    After installing this module you should execute the following script in
    order to preserve your secondary language strings, i.e., Your secondary
    language is the one to be shown in the Product Names

    UPDATE product_template
    SET name = subview.new_name
    FROM (
    SELECT pt.id AS tmpl_id, pt.name AS old_name, it.value AS new_name
    FROM product_template pt
    INNER JOIN ir_translation it ON (pt.id = it.res_id)
    WHERE it.name = 'product.template,name'
    AND it.value <> pt.name
    ) subview
    WHERE subview.tmpl_id = id;

    UPDATE product_product
    SET name_template = subview.new_name_template
    FROM (
    SELECT pp.id AS product_id, pp.name_template AS old_name_template,
    pt.name AS new_name_template
    FROM product_product pp
    INNER JOIN product_template pt ON pp.product_tmpl_id = pt.id
    WHERE pp.name_template <> pt.name
    ) subview
    WHERE subview.product_id = id;

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
