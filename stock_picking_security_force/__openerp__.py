{
    "name" : "stock_picking_security_force",
    "version" : "1.1",
    "author" : "Vauxoo",
    "website" : "www.vauxoo.com",
    "category" : "Stock",
    "description" : """ Add security to the button Force Availability, module stock.picking """,
    "init_xml" : [],
    "depends" : ["stock"],
    "update_xml" : [
        'stock_picking_security_force_view.xml',
        'security/groups.xml'
        ],
    "demo_xml" : [],
    "test" : [],
    "installable" : True,
    "auto_install" : False,
}
