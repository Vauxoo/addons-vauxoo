# -*- encoding: utf-8 -*-
{
    "name" : "Sale report for AMD Consorcium",
    "version" : "0.1",
    "depends" : ["sale", "multireport_base"],
    "author" : "Vauxoo",
    "description" : """
    What do this module:
    Just the quotation format.
                    """,
    "website" : "http://vauxoo.com",
    "category" : "Generic Modules/Sales",
    "init_xml" : [
    ],
    "demo_xml" : [
    ],
    "update_xml" : [
        "wizard/sale_order_multicompany.xml",
        "sale_multicompany_report_view.xml",
        "sale_order_view.xml",

    ],
    "active": False,
    "installable": False,
}
