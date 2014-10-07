# -*- coding: utf-8 -*-
#
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
{
    "name": "Expired Task Information", 
    "version": "0.1", 
    "author": "Vauxoo", 
    "category": "Project", 
    "description": """
Information about status tasks
==============================
It's very important know status for our tasks, details like  when it's expire?
When was the last change? And other important info for project management  and
task personal control.

For this management we create this module, that  verify the task status
automatically  and sends emails if finds something relevant in task

Technical features
---------------------------
Created a new model to add configuration for the sending emails with the task
status. To access in this module you need have access rule and is in the setup
menu of projects. In this module you can configure the day number before the
expire date to send  email reporting it, and also the day number that a task
must have without changes(Taking like changes, work summary or messages in the
task)""", 
    "website": "http://www.vauxoo.com", 
    "license": "", 
    "depends": [
        "base", 
        "project"
    ], 
    "demo": [], 
    "data": [
        "security/config_task_security.xml", 
        "security/ir.model.access.csv", 
        "view/task_expiry_config_view.xml", 
        "data/config_task_expired_data.xml"
    ], 
    "test": [], 
    "js": [], 
    "css": [], 
    "qweb": [], 
    "installable": True, 
    "auto_install": False, 
    "active": False
}