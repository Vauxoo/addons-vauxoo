#!/usr/bin/python
# -*- enconding: utf-8 -*-


{
	"name" : "sprint_kanban",#Module's name
	"version" : "1.1",	#Version's number
	"depends" :  ['project','web_kanban'],	#Dependent module
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
					"view/sprint_kanban_view.xml",
	                 ],
	"installable" : True,
	"active" : False

}
