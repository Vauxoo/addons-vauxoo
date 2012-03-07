# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2008 ACYSOS S.L. (http://acysos.com) All Rights Reserved.
#                       Pedro Tarrafeta <pedro@acysos.com>
#    Copyright (c) 2008 Pablo Rocandio. All Rights Reserved.
#    $Id$
#    Modificado para cumplir con legislacion Venezolana por
#    Netquatro, C.A. <openerp@netquatro.com>
##############################################################################

{
    "name" : "Formatos Nota de Entrega y Guia Despacho",
    "version" : "0.3",
    "author" : "Pablo Rocandio y ACYSOS, S.L., Ajustado para Venezuela Netquatro, C.A.",
    "category" : "Localisation/Venezuela",
    "description": """
    Notas de entrega
    Guías de despacho según decreto 
    0591
    Referencia Legal:
    http://wiki.openerp.org.ve/index.php?title=0591
    """,
    "license" : "GPL-3",
    "depends" : ["stock_valued"],
    "init_xml" : [],
    "update_xml" : [
        'stock_valued_sequence.xml',
        'stock_valued_view.xml',
        'stock_valued_report.xml',
        'stock_valued_wizard.xml',
                   ],
    "active": False,
    "installable": True,
    "website": "http://openerp.netquatro.com",
}




