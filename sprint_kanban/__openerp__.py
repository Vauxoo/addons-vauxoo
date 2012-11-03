#!/usr/bin/python
# -*- enconding: utf-8 -*-


{
	"name" : "sprint_kanban",#Module's name
	"version" : "1.1",	#Version's number
	"depends" :  [  'project',
				'web_kanban',
				'base_setup',
				'base_status',
				'product',
				'analytic',
				'board',
				'mail',
				'resource',],	#Dependent module
	"author" : "Luis Torres",#Programmer
	"description" : """
	This is a module of the sprint kanban
	""", #Description of the module
	"website" : "http://vauxoo.com",#Website
	"category" : "Test",#Category for general information
	"init_xml" : [],#Init data
	"demo_xml" : [],#Demo data
	"test" : [],#Load, yaml
	"update_xml" : [
					'security/security_sprint_kanban.xml','security/ir.model.access.csv',
					"view/sprint_kanban_view.xml","view/sprint_prueba_view.xml"
	                 ],
	"installable" : True,
	"active" : False

}
