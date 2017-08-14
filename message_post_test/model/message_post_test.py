# coding: utf-8
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

from odoo import models, fields


class MessagePostTestNewApi(models.Model):

    _name = 'message.post.test.new.api'
    _inherit = ['mail.thread']

    name = fields.Char('Name')
    user_id = fields.Many2one('res.users', 'User')
    number = fields.Integer('Number')
    line_ids = fields.One2many('message.post.test.line.new.api', 'test_id',
                               'Lines')
    user_ids = fields.Many2many('res.users', 'test_user_table_new_api',
                                'test_id', 'user_id', 'Users')
    select = fields.Selection([('1', 'Testing'), ('2', 'Changed')],
                              'Selection')
    check = fields.Boolean('Check')


class MessagePostTestLineNewApi(models.Model):

    _name = 'message.post.test.line.new.api'

    name = fields.Char('Name')
    number = fields.Integer('Number')
    check = fields.Boolean('Check')
    test_id = fields.Many2one('message.post.test.new.api', 'Test')
