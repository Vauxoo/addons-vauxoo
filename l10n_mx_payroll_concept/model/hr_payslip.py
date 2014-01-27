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

class hr_payslip(osv.osv):

    _inherit = 'hr.payslip'

    def onchange_employee_id(self, cr, uid, ids, date_from, date_to, employee_id=False, contract_id=False, context=None):
        rule_input_line_obj = self.pool.get('hr.rule.input')
        data = super(hr_payslip, self).onchange_employee_id(cr, uid, ids, date_from, date_to, employee_id=employee_id, contract_id=contract_id, context=context)
        data_input_line_ids = data.get('value').get('input_line_ids')
        if data_input_line_ids:
            for line in data_input_line_ids:
                line_id = rule_input_line_obj.search(cr, uid, [('code','=',line.get('code')),('name','=',line.get('name'))],context=context)
                line_data_id = rule_input_line_obj.browse(cr, uid, line_id[0], context=context).input_id.id
                line.update({'salary_rule_id': line_data_id})
        return data 
