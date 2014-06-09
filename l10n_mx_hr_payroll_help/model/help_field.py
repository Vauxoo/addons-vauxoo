#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: vauxoo consultores (info@vauxoo.com)
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
################################################################################

from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
from openerp import pooler, tools

class hr_employee(osv.Model):

    _inherit = 'hr.employee'

    _columns = {
        'identification_id': fields.char('Identification No', size=32, help=_('Attribute to express the employee number from 1 to 15 positions')),
        'department_id':fields.many2one('hr.department', 'Department', help=_('Attribute to the expression of the department or area that belongs the worker')),
    }


class hr_contract(osv.Model):

    _inherit = 'hr.contract'

    _columns = {
        'date_start': fields.date(_('Date of employment'), required=True, help=_('Attribute to express the start date of the employment relationship between employer and employee')),
        'job_id': fields.many2one('hr.job', 'Job Title', help=_('Rank  assigned to the employee or activity you do')),
        'type_id': fields.many2one('hr.contract.type', "Contract Type", required=True, help=_('Contract type having the worker: Base, Eventually, Trust, Unionized, test, etc.')),
        'schedule_pay': fields.selection([
            ('monthly', 'Monthly'),
            ('quarterly', 'Quarterly'),
            ('semi-annually', 'Semi-annually'),
            ('annually', 'Annually'),
            ('weekly', 'Weekly'),
            ('bi-weekly', 'Bi-weekly'),
            ('bi-monthly', 'Bi-monthly'),
            ('fortnightly', _('Fortnightly')),
            ], 'Scheduled Pay', select=True, help=_('Way in which the payment of the wage is set: daily, weekly, biweekly, monthly, bimonthly, commission, etc.')),
        'wage': fields.float('Wage', digits=(16,2), required=True, help=_("Remuneration granted to the employee, which is composed by payments made in cash daily fee, gratuities, perceptions, food, housing, bonuses, commissions, benefits in kind and any other amount or benefit provided to the employee for their work.")),
    }


class hr_payslip(osv.Model):

    _inherit = 'hr.payslip'

    _columns = {
        'date_from': fields.date('Date From', readonly=True, states={'draft': [('readonly', False)]}, required=True, help=_('Attribute to the expression of the initial payment date')),
        'date_to': fields.date('Date To', readonly=True, states={'draft': [('readonly', False)]}, required=True, help=_('Attribute to the expression of the final date of payment')),
        'worked_days_line_ids': fields.one2many('hr.payslip.worked_days', 'payslip_id', 'Payslip Worked Days', required=False, readonly=True, states={'draft': [('readonly', False)]}, help=_('Attribute to the expression of the number of days paid')),
    }
