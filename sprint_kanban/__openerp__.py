#!/usr/bin/python
# -*- enconding: utf-8 -*-
{
    "name": "Sprint Kanban", 
    "version": "1.1", 
    "author": "Vauxoo", 
    "category": "Project", 
    "description": """
This is a module of the sprint kanban
"name" : "Sprint Kanban",#Module's name
"version" : "1.1",\t#Version's number
'resource',],\t#Dependent module
 #Description of the module
 "website" : "http://vauxoo.com",#Website
""", 
    "website": "http://vauxoo.com", 
    "license": "", 
    "depends": [
        "project", 
        "web_kanban", 
        "base_setup", 
        "base_status", 
        "product", 
        "analytic", 
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
    "auto_install": False
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
