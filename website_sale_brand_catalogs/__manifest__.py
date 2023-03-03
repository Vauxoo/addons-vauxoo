{
    "name": "Brand Catalogs for Website Sale",
    "summary": """
    This module manage the brands catalogs for products
    """,
    "category": "Website/Website",
    "version": "15.0.1.0.0",
    "author": "Vauxoo",
    "license": "LGPL-3",
    "depends": [
        "crm",
        "product_brand",
        "website_sale",
    ],
    "demo": [
        "demo/product_brand_demo.xml",
        "demo/product_brand_attachment_demo.xml",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_attachment_data.xml",
        "data/settings.xml",
        "data/website_menu_data.xml",
        "views/templates/brand_header_template.xml",
        "views/product_brand_attachment_views.xml",
        "views/pages/catalogs.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "website_sale_brand_catalogs/static/src/scss/variables.scss",
            "website_sale_brand_catalogs/static/src/scss/catalog.scss",
            "website_sale_brand_catalogs/static/src/js/catalog_section.js",
        ],
        "web.assets_tests": [
            "website_sale_brand_catalogs/static/tests/tours/test_catalog.js",
        ],
    },
    "installable": False,
    "application": True,
    "auto_install": False,
}
