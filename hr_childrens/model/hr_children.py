# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: Luis Ernesto García Medina (ernesto_gm@vauxoo.com)
############################################################################
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
"""File to add fields date_start and children_ids in hr.employee, and the
attributes to childrens of employee.
"""
from openerp.osv import osv, fields


class HrEmployee(osv.Model):
    """Inherit hr_employee to add date_start and to add yours childrens
    """
    _inherit = "hr.employee"

    _columns = {
        'date_start': fields.date('Date Start'),
        'children_ids': fields.one2many(
            'hr.children', 'employee_id', 'Childrens')
    }


class HrChildren(osv.Model):
    """Class to add object of childrens to employee
    """
    _name = "hr.children"

    _order = 'name'

    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'date_of_birth': fields.date('Date of birth'),
        'schooling': fields.selection(
            [('elementary', 'Elementary'),
             ('high_school', 'High School'),
             ('preparatory', 'Preparatory'),
             ('university', 'University')], 'Schooling'),
        'employee_id': fields.many2one('hr.employee', 'Employee')
    }
