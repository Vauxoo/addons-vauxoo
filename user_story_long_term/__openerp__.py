# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
############# Credits #########################################################
#    Coded by: Yanina Aular <yani@vauxoo.com>
#    Planified by: Maria Gabriela Quilarque <gabriela@vauxoo.com>
#    Audited by: Maria Gabriela Quilarque <gabriela@vauxoo.com>
###############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################
#'user_story_long_term_demo.xml'
#'data/user_story_template.xml',
#'wizard/user_story_compute_phases_view.xml',
#'wizard/user_story_compute_tasks_view.xml',
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
{
    "name": "Long Term User Story",
    "version": "1.6",
    "author": "Vauxoo",
    "category": "User Story Management",
    "website": "http://www.vauxoo.com",
    "license": "",
    "depends": [
        "base",
        "mail",
        "user_story",
        "project_conf",
        "project_long_term"
    ],
    "demo": [
        "demo/user_story_conf.xml"
    ],
    "data": [
        "security/ir.model.access.csv",
        "user_story_long_term_view.xml",
        "workflow/user_story_long_term_workflow.xml"
    ],
    "test": [],
    "js": [],
    "css": [],
    "qweb": [],
    "installable": True,
    "auto_install": False,
    "active": False
}
