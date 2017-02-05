# coding: utf-8
#
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2014 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#
#    Coded by: Luis Torres (luis_t@vauxoo.com)
#
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
#
"""File to inherit hr.employee and added fields to complete name
"""
from odoo import models, fields, api


class HrEmployee(models.Model):
    """Inherit hr.employee to added fields to complete name
    """
    _inherit = 'hr.employee'

    @api.one
    @api.depends('name', 'second_name', 'last_name', 'second_last_name')
    def _get_full_name(self):
        """Method to concatenate last_name, second_last_name, name & second_name
        in a new field function
        """
        emp = self
        emp.complete_name = (emp.last_name or '') + ' ' + (
            emp.second_last_name or '') + ' ' + (emp.name or '') + ' ' + (
            emp.second_name or '')

    @api.one
    @api.depends('name', 'second_name')
    def _get_full_first_name(self):
        emp = self
        emp.full_first_name = (emp.name or '') + ' ' + (emp.second_name or '')

    @api.one
    @api.depends('last_name', 'second_last_name')
    def _get_full_last_name(self):
        emp = self
        emp.full_last_name = (emp.last_name or '') + ' ' + (
                emp.second_last_name or '')

    second_name = fields.Char(
        'Second Name', help='Second employee name')
    last_name = fields.Char(
        'Last Name', help='Last employee name')
    second_last_name = fields.Char(
        'Second Last Name', help='Second employee last name')
    couple_last_name = fields.Char(
        'Couple Last Name', help='Last name of employee couple')
    complete_name = fields.Char(
        'Full Name',
        compute='_get_full_name',
        help='Full name of employee, conformed by: Last \
        name + Second last name + Name + Second Name')
    full_first_name = fields.Char(
        'Full First Name',
        compute='_get_full_first_name',
        help='Full firs name of employee, conformed by: \
        Name + Second Name')
    full_last_name = fields.Char(
        'Full last Name',
        compute='_get_full_last_name',
        help='Full last name of employee, conformed by: \
        Last name + Second last name')
