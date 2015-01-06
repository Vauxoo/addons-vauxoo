#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###########################################################################
#   Credits:
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


class message_post_test_line(osv.Model):

    _name = 'message.post.test.line'

    _columns = {
        'name': fields.char('Name'),
        'number': fields.integer('Number'),
        'check': fields.boolean('Check'),
        'test_id': fields.many2one('message.post.test', 'Test'),
    }


class message_post_test(osv.Model):

    _name = 'message.post.test'
    _inherit = ['message.post.show.all']

    _columns = {
        'name': fields.char('Name'),
        'user_id': fields.many2one('res.users', 'User'),
        'number': fields.integer('Number'),
        'line_ids': fields.one2many('message.post.test.line', 'test_id',
                                    'Lines'),
        'user_ids': fields.many2many('res.users', 'test_user_table', 'test_id',
                                     'user_id', 'Users'),
        'check': fields.boolean('Check'),
    }
