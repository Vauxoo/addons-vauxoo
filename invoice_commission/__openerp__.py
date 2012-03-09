# -*- encoding: utf-8 -*-
{
    "name" : "Account invoice Update",
    "version" : "0.1",
    "depends" : ["account","baremo"],
    "author" : "Vauxoo",
    "description" : """
    What do this module:
    Update account module to show invoice commission 
                    """,
    "website" : "http://vauxoo.com",
    "category" : "Generic Modules/Accounting",
    "init_xml" : [
    ],
    "update_xml" : [
        "view/invoice_commission_view.xml",
    ],
    "active": False,
    "installable": True,
}
