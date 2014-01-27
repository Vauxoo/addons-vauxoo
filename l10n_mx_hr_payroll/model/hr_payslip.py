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

class hr_payslip_overtime(osv.osv):
    '''
    Payslip Overtime
    '''

    _name = 'hr.payslip.overtime'
    _description = 'Payslip Overtime'
    _columns = {
        'name': fields.char('Description', size=256, required=True),
        #~ 'code':fields.char('Code', size=64, required=True),
        #~ 'category_id':fields.many2one('hr.salary.rule.category', 'Category', required=True),
        'payslip_id': fields.many2one('hr.payslip', 'Pay Slip', required=True, ondelete='cascade', select=True),
        'sequence': fields.integer('Sequence', required=True, select=True),
        'number_of_days': fields.integer('Number of Days', help="Number of days in which the employee performed overtime in the period",required=True),
        'number_of_hours': fields.integer('Number of Hours', help="Number of overtime hours worked in the period",required=True),
        'type_hours': fields.selection([('double', 'Double'),('triples', 'Triples'), ], "Type of Hours", required=True, help='Type of payment of overtime: double or triple'),
        'amount': fields.float('Amount', help="Amount paid for overtime", required=True),
    }
    _order = 'payslip_id, sequence'
    _defaults = {
        'sequence': 10,
        'amount': 0.0,
    }

hr_payslip_overtime()
    
class hr_payslip_inability(osv.osv):
    '''
    Payslip Inability
    '''

    _name = 'hr.payslip.inability'
    _description = 'Payslip Inability'
    _columns = {
        'payslip_id': fields.many2one('hr.payslip', 'Pay Slip', required=True, ondelete='cascade', select=True),
        'sequence': fields.integer('Sequence', required=True, select=True),
        #~ 'code':fields.char('Code', size=64, required=True),
        #~ 'category_id':fields.many2one('hr.salary.rule.category', 'Category', required=True),
        'number_of_days': fields.integer('Number of Days', help="Number of days in which the employee performed inability in the period",required=True),
        'inability_id': fields.many2one('payroll.hr.inability', 'Inability', required=True, select=True, help="Reason for inability: Catalog published in the Internet portal of the SAT"),
        'amount': fields.float('Amount', help="Amount of discount for the inability", required=True),
    }
    _order = 'payslip_id, sequence'
    _defaults = {
        'sequence': 10,
        'amount': 0.0,
    }

hr_payslip_inability()

class hr_payslip(osv.osv):
    '''
    Pay Slip
    '''

    _inherit = 'hr.payslip'
    _columns = {
        'overtime_line_ids': fields.one2many('hr.payslip.overtime', 'payslip_id', 'Payslip Overtime', required=False, readonly=True, states={'draft': [('readonly', False)]}, help="Optional node to express the applicable overtime"),
        'inability_line_ids': fields.one2many('hr.payslip.inability', 'payslip_id', 'Payslip Inability', required=False, readonly=True, states={'draft': [('readonly', False)]}, help="Optional node to express disabilities applicable"),
    }
