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

class hr_payslip_input(osv.osv):

    _inherit = 'hr.payslip.input'
    _columns = {
       'salary_rule_id' : fields.many2one('hr.salary.rule', 'Salary Rule', required=True,),
       'exempt_amount': fields.float('Exempt Amount', help='Required attribute represents the exempt amount of a concept of perception or deduction.'),
    }

    def onchange_salary_rule(self, cr, uid, ids, salary_rule_id=False, parent_id=False, context=None):
        if context is None:
            context={}
        ids = isinstance(ids, (int, long)) and [ids] or id
        hr_salary_rule_obj = self.pool.get('hr.salary.rule')
        result = {'name': False,'code': False, 'contract_id': False}
        if salary_rule_id:
            read_salary_data = hr_salary_rule_obj.browse(cr, uid, salary_rule_id, context=context) or False
            if read_salary_data and read_salary_data.input_ids and read_salary_data.input_ids[0]:
                result['name'] = read_salary_data.input_ids[0].name
                result['code'] = read_salary_data.input_ids[0].code
                result['contract_id'] = parent_id
                return {'value': result} 
        return {'value': result} 

