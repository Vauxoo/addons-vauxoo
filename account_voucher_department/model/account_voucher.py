#!/usr/bin/python
# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
############# Credits #########################################################
#    Coded by: Katherine Zaoral <kathy@vauxoo.com>
#    Planified by: Humberto Arocha <hbto@vauxoo.com>
#    Audited by: Humberto Arocha <hbto@vauxoo.com>
###############################################################################
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
###############################################################################

from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
from openerp import tools


class account_voucher(osv.Model):

    _inherit = 'account.voucher'
    _columns = {
        'department_id': fields.many2one(
            'hr.department',
            string='Department',
            help='Department were the requester belongs.'),
    }

    def onchange_employee_id(self, cr, uid, ids, employee_id, context=None):
        """ Return the department depending of the employee.
        @param employee_id: employee id
        """
        context = context or {}
        res = {}
        he_obj = self.pool.get('hr.employee')
        if employee_id:
            he_brw = he_obj.browse(cr, uid, employee_id, context=context)
            department_id = (he_brw.department_id and he_brw.department_id.id
                or False)
            res.update({'value': {'department_id': department_id}})
        return res
