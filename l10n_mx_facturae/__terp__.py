# -*- encoding: utf-8 -*-
{
    "name" : "Creacion de Factura Electronica para Mexico (CFD)",
    "version" : "1.0",
    "author" : "moylop260@hotmail.com",
    "category" : "Localisation/Accounting",
    "description" : """This module creates e-invoice files from invoices with standard of Mexican SAT.
Requires the following programs:
  xsltproc
    Ubuntu insall with:
        sudo apt-get install xsltproc
  
  openssl
      Ubuntu insall with:
        sudo apt-get install openssl
    """,
    "website" : "http://moylop.blogspot.com/",
    "license" : "AGPL-3",
    "depends" : ["account", "base_vat", "document", 
            "sale",#no depende de "sale" directamente, pero marca error en algunas versiones
        ],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
        'security/ir.model.access.csv',
        "l10n_mx_facturae_report.xml",
        "l10n_mx_facturae_wizard.xml",
        "ir_sequence_view.xml",
        "res_company_view.xml",
        "invoice_view.xml"
    ],
    "installable" : True,
    "active" : False,
}
