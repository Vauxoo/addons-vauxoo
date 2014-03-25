#!/usr/bin/python
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

{
    'name': 'Long Term User Story',
    'version': '1.0',
    'author': 'Vauxoo',
    'website': 'http://www.vauxoo.com',
    'category': 'User Story Management',
    'depends': ['base', 'mail', 'user_story', 'project_conf'],
    'description': """
Long Term User Story Management module that tracks planning, scheduling, resources allocation.
==============================================================================================

Features:
---------
    * Define various Phases of Project
    * Compute Phase Scheduling: Compute start date and end date of the phases
      which are in draft, open and pending state of the project given. If no
      project given then all the draft, open and pending state phases will be taken.
    * Compute Task Scheduling: This works same as the scheduler button on
      project.phase. It takes the project as argument and computes all the open,
      draft and pending tasks.
    * Schedule Tasks: All the tasks which are in draft, pending and open state
      are scheduled with taking the phase's start date.
    """,
    'demo': [
        #'user_story_long_term_demo.xml'
        'demo/user_story_conf.xml',
        ],
    'test': [],
    'data': [
        #'security/ir.model.access.csv',
        'user_story_long_term_view.xml',
        'workflow/user_story_long_term_workflow.xml',
        'data/user_story_template.xml',
        #'wizard/user_story_compute_phases_view.xml',
        #'wizard/user_story_compute_tasks_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
