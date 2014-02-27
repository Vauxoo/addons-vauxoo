# -*- coding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: Rodo (rodo@vauxoo.com)
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
from openerp.osv import osv, fields


class hr_department(osv.Model):
    _inherit = "hr.department"

    _columns = {
        'analytic_account_id': fields.many2one('account.analytic.account',
                                               'Analytic'),
    }


class hr_expense_line(osv.Model):
    _inherit = "hr.expense.line"

    def _get_analytic(self, cr, uid, context={}):
        if context['depto']:
            depto = self.pool.get('hr.department').browse(
                cr, uid, [context['depto']])[0]
            return depto.analytic_account_id.id
        return False

    _defaults = {
        'analytic_account': _get_analytic
    }
