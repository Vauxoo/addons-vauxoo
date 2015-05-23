# -*- enconding: utf-8 -*-
{
    "name": "Sprint Kanban", 
    "version": "1.1", 
    "author": "Vauxoo", 
    "category": "Project", 
    "description": """
\tThis is a module of the sprint kanban
\t""", 
    "website": "http://vauxoo.com", 
    "license": "", 
    "depends": [
        "project", 
        "web_kanban", 
        "base_setup", 
        "base_status", 
        "product", 
        "analytic", 
        "portal", 
        "board", 
        "mail", 
        "resource"
    ], 
    "demo": [], 
    "data": [
        "security/security_sprint_kanban.xml", 
        "security/ir.model.access.csv", 
        "view/sprint_kanban_view.xml", 
        "view/project_view.xml"
    ], 
    "test": [], 
    "js": [], 
    "css": [], 
    "qweb": [], 
    "installable": True, 
    "auto_install": False, 
    "active": False
}
