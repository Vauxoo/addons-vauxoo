#!/usr/bin/python
# -*- enconding: utf-8 -*-


{
	"name" : "Sprint Kanban",#Module's name
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
	"author" : "Vauxoo",
	"description" : """
	This is a module of the sprint kanban
	""", #Description of the module
	"website" : "http://vauxoo.com",#Website
	"category" : "Project",
	"init_xml" : [],
	"demo_xml" : [],
	"test" : [],
	"update_xml" : [
					'security/security_sprint_kanban.xml','security/ir.model.access.csv',
					"view/sprint_kanban_view.xml",
					"view/project_view.xml",
	                 ],
	"installable" : True,
	"active" : False

}
