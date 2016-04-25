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
from openerp.osv import osv, fields


class HrEmployee(osv.Model):
    """Inherit hr.employee to added fields to complete name
    """
    _inherit = 'hr.employee'

    def _get_full_name(self, cr, uid, ids, fields_name, args, context=None):
        """Method to concatenate last_name, second_last_name, name & second_name
        in a new field function
        """
        if context is None:
            context = {}
        res = {}
        for emp in self.browse(cr, uid, ids, context=context):
            res[emp.id] = (emp.last_name or '') + ' ' + (
                emp.second_last_name or '') + ' ' + (emp.name or '') + ' ' + (
                emp.second_name or '')
        return res

    def _update_fill_name(self, cr, uid, ids, context=None):
        """Method call function
        """
        return ids

    def _get_full_first_name(self, cr, uid, ids, fields_name, args,
                             context=None):
        if context is None:
            context = {}
        res = {}
        for emp in self.browse(cr, uid, ids, context=context):
            res[emp.id] = (emp.name or '') + ' ' + (emp.second_name or '')
        return res

    def _get_full_last_name(self, cr, uid, ids, fields_name, args,
                            context=None):
        if context is None:
            context = {}
        res = {}
        for emp in self.browse(cr, uid, ids, context=context):
            res[emp.id] = (emp.last_name or '') + ' ' + (
                emp.second_last_name or '')
        return res

    _columns = {
        'second_name': fields.char(
            'Second Name', help='Second employee name'),
        'last_name': fields.char(
            'Last Name', help='Last employee name'),
        'second_last_name': fields.char(
            'Second Last Name', help='Second employee last name'),
        'couple_last_name': fields.char(
            'Couple Last Name', help='Last name of employee couple'),
        'complete_name': fields.function(
            _get_full_name, string='Full Name', type='char', store={
                'hr.employee': (_update_fill_name, [
                    'name', 'second_name', 'last_name', 'second_last_name'],
                    50),
            }, method=True, help='Full name of employee, conformed by: Last \
            name + Second last name + Name + Second Name'),
        'full_first_name': fields.function(
            _get_full_first_name, string='Full First Name', type='char',
            store={
                'hr.employee': (
                    _update_fill_name, ['name', 'second_name'], 50),
            }, method=True, help='Full firs name of employee, conformed by: \
            Name + Second Name'),
        'full_last_name': fields.function(
            _get_full_last_name, string='Full last Name', type='char', store={
                'hr.employee': (_update_fill_name, [
                    'last_name', 'second_last_name'], 50),
            }, method=True, help='Full last name of employee, conformed by: \
            Last name + Second last name'),
    }
