# -*- encoding: utf-8 -*-
#
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#
#    Coded by: Jorge Angel Naranjo (jorge_nr@vauxoo.com)
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

from openerp.tools.translate import _
from openerp.osv import fields, osv


class payroll_working_day(osv.Model):

    _name = "payroll.working.day"

    _columns = {
        'name': fields.char('Description', size=256, required=True,help='Type working day that covers the worker: Day, night, mixed per hour, reduced, continued heading, by turns, etc..'),
    }
    
class hr_contract(osv.Model):

    _inherit = "hr.contract"

    _columns = {
        'working_day_id': fields.many2one('payroll.working.day', 'Type of working day',help='Type working day that covers the worker: Day, night, mixed per hour, reduced, continued heading, by turns, etc..'),
        'integrated_salary': fields.float('Integrated Salary',required=True, help='Integrated Salary'),
        'seniority': fields.integer('Seniority', help="Number of weeks that the employee has maintained relationships employment with the employer"),
    }
