{
    "name" : "mrp_production_security_force",
    "version" : "1.1",
    "author" : "Vauxoo",
    "website" : "www.vauxoo.com",
    "category" : "MRP",
    "description" : """ Add security to the button Force Availability, module mrp """,
    "init_xml" : [],
    "depends" : ["mrp"],
    "update_xml" : [
        'mrp_production_security_force_view.xml',
        'security/groups.xml'
        ],
    "demo_xml" : [],
    "test" : [],
    "installable" : True,
    "auto_install" : False,
}
