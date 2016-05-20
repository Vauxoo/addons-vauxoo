# coding: utf-8
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
# ##############Credits######################################################
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
    "name": "User Story",
    "version": "8.0.0.3.0",
    "author": "Vauxoo",
    "category": "Generic Modules",
    "website": "http://vauxoo.com",
    "license": "",
    "depends": [
        "base",
        "project",
        "sprint_kanban",
        "project_timesheet",
        "hr_timesheet_invoice",
        "project_conf",
        "report_webkit"
    ],
    "demo": [
        "demo/demo.xml"
    ],
    "data": [
        # "data/data_us_report.xml",
        # "report/user_story_report_view.xml",
        "security/userstory_security.xml",
        "security/ir.model.access.csv",
        "view/userstory_view.xml",
        "view/project_view.xml",
        "view/hr_timesheet_view.xml",
        "view/hr_timesheet_all_view.xml",
        "view/custom_project_task_view.xml",
        "view/account_analytic_account.xml",
        "data/data.xml",
        "data/user_story_template.xml",
        "report/user_story_report.xml"
    ],
    "test": [],
    "js": [],
    "css": [
        "static/src/css/*.css"
    ],
    "qweb": [],
    "installable": True,
    "auto_install": False,
}
