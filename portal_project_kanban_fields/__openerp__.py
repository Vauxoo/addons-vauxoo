#!/usr/bin/python
# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
############# Credits #########################################################
#    Coded by: Yanina Aular <yanina.aular@vauxoo.com>
#    Planified by: Humberto Arocha <hbto@vauxoo.com>
#    Audited by: Humberto Arocha <hbto@vauxoo.com>
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

{
    'name': 'Portal Project Kanban Fields',
    'version': '1.0',
    'author': 'Vauxoo C.A.',
    'website': 'http://www.openerp.com.ve',
    'category': '',
    'description': '''
Add three fields to the project.

- Project URL: Link to the project in launchpad.
- Documentation URL: Link to the project documentation.
- Image: Logo of the Project
    ''',
    'depends': ['base', 'project', 'portal_project'],
    'data': [
        'view/project_view.xml',
        ],
    'demo': [],
    'test': [],
    'active': False,
    'installable': True,
    'css':[
        'static/src/css/project.css',
        ],
}
