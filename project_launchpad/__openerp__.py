#-*- coding:utf-8 -*-
#
#
#    OpenERP, Open Source Management Solution
#    Copyright (C)2010-  OpenERP SA (<http://openerp.com>). All Rights Reserved
#
#    Financed by Vauxoo
#    Developed by Oscar Alcala <oszckar@gmail.com>
#
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
#
{
    "name": "Project Launchpad",
    "version": "1.0",
    "author": "Vauxoo",
    "website": "http://www.vauxoo.com",
    "category": "Tools",
    "depends": [
            "project",
            "portal_project_imp",
                ],
    "description": """
        This module gets data from launchpad projects to OpenERP projects
        the main pourpose of this feature is to have your CMS projects up
        to date and consistent with the projects you acctually work on.

        Please install launchpadlib from the Python package index or from
        ubuntu repositories via apt-get
    """,
    "init_xml": [],
    "demo_xml": [],
    "test": [],
    "update_xml": [
                   "views/project_launchpad_view.xml",
                    ],
    'installable': True,
    'active': False,
    'certificate': None,
}
