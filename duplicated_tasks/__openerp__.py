# -*- coding: utf-8 -*-
##############################################################################
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
##############################################################################
{
    'name': 'Duplicated Tasks',
    'version': '0.1',
    'author': 'Vauxoo',
    'category': 'Projects',
    'description': """

Identify when a task could be duplicated
========================================

In task model we add 2 action to control when a task could have any task
similar

-First:

When you create the task and adds name you have a button that will search task
name or description similars to the name set in the new task and you can select
the task that you think that could be the same task

-Second:

We add the action menu in task model, where you can search task, with some
specific words that could match with other task, to avoid create a duplicated
task
    """,
    'website': 'http://www.vauxoo.com',
    'images': [],
    'depends': [
        'project',
    ],
    'data': [
        'wizard/search_duplicated_task_view.xml',
        'view/task_view.xml',
    ],
    'js': [
    ],
    'qweb': [
    ],
    'css': [
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
