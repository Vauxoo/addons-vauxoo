# coding: utf-8
# © 2015 Vauxoo - http://www.vauxoo.com
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# info Vauxoo (info@vauxoo.com)
# coded by: luis_t@vauxoo.com

# TODO: Migrate, it is a feature (check first if not available on V11.0)
# Note that procurements are not anymore the ones creating automatic MO.

{
    "name": "MRP Responsible",
    "version": "12.0.1.0.0",
    "author": "Vauxoo",
    "category": "Generic Modules/Product",
    "website": "http://Vauxoo.com",
    "license": "",
    "depends": [
        "mrp",
    ],
    "demo": [],
    "data": [
        "views/mrp_view.xml",
        "views/product_view.xml",
    ],
    "installable": True,
    "auto_install": False,
}
