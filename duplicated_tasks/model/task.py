# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: Vauxoo C.A.
#    Planified by: Nhomar Hernandez
#    Audited by: Vauxoo C.A.
#############################################################################
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
##########################################################################

from openerp.osv import osv, fields


class InheritTask(osv.Model):

    """Inherit project task module to add description fields  when a task is
        duplicated"""

    _inherit = 'project.task'

    _columns = {
        'duplicated': fields.boolean('Duplicated',
                                     help='True if this task is duplicated '
                                     'you can see the parent task in '
                                     'parent task field '),
        'duplicated_task_id': fields.many2one('project.task',
                                              'Parent Task',
                                              help='This is the main task '
                                              'of which this is a '
                                              'copy'),
    }
