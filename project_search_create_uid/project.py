# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-today OpenERP SA (<http://www.openerp.com>)
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


from openerp.osv import fields, osv


class project_task(osv.Model):
    _inherit = 'project.task'

    _columns = {
        'write_date': fields.datetime('Date Modified', readonly=True),
        'write_uid': fields.many2one('res.users', 'Last Modification User', readonly=True),
        'create_date': fields.datetime('Date Created', readonly=True),
        'create_uid': fields.many2one('res.users', 'Creator', readonly=True),
        'date_from_create': fields.dummy(string="Create Date From", type='date'),
        'date_to_create': fields.dummy(string="Create Date To", type='date'),
        'date_from_write': fields.dummy(string="Write Date From", type='date'),
        'date_to_write': fields.dummy(string="Write Date To", type='date'),
    }
