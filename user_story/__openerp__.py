##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
###############Credits######################################################
#    Coded by: Vauxoo C.A. (Yanina Aular & Miguel Delgado)          
#    Planified by: Rafael Silva
#    Audited by: Vauxoo C.A.
##############################################################################
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
##############################################################################

{
    "name" : "User Story",
    "version" : "0.1",
    "depends" : ["base","project","sprint_kanban"],
    "author" : ["Vauxoo",],
    "description" : """
    What do this module:
    Este módulo registra requerimientos funcionales y técnicos de software a través de Historias de Usuarios. 
    
    Las historias se redactan siguiendo preceptos de las prácticas ágiles, y mas específicamente de una recomendación de Dan North
    en su artículo 'What's in a Story?'. Este artículo representa la documentación funcionalde este módulo. Las fuentes en inglés
    y español el artículo son las siguientes:
    
    http://dannorth.net/whats-in-a-story/
    http://adrianmoya.com/2012/08/que-hay-en-una-historia/
                    """,
    "website" : "http://vauxoo.com",
    "category" : "Generic Modules",
    "init_xml" : [
    ],
    "demo_xml" : [
    ],
    "update_xml" : [
        "report/ir_report.xml",
        "security/userstory_security.xml",
        "security/ir.model.access.csv",
        "view/userstory_view.xml",
    ],
    "active": False,
    "images": [],
    "installable": True,
}
