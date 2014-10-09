#!/usr/bin/python
# -*- enconding: utf-8 -*-
{
	"name" : "Sprint Kanban",
	"version" : "1.1",
	"depends" :  [  'project',
				'web_kanban',
				'base_setup',
				'product',
				'analytic',
				'board',
				'mail',
				'resource',],
	"author" : "Vauxoo",
	"description" : """
	This is a module of the sprint kanban
	""",
	"website" : "http://www.vauxoo.com",
	"category" : "Project",
	"test" : [],
	"data" : [
					'security/security_sprint_kanban.xml','security/ir.model.access.csv',
					"view/sprint_kanban_view.xml",
					"view/project_view.xml",
	                 ],
	"installable" : True,
	"active" : False
}
