#!/usr/bin/python
# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
############# Credits #########################################################
#    Coded by: Yanina Aular <yani@vauxoo.com>
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

import time
from lxml import etree

from openerp.osv import fields, osv
from openerp import tools
from openerp.tools.translate import _

class account_analytic_group(osv.Model):
    _name = 'account.analytic.group'

    _columns = {
            'name' : fields.char('Name', required=True, size=128),
            }

class account_analytic_account(osv.Model):
    _inherit = 'account.analytic.account'

    _columns = {
        'analytic_group_id': fields.many2one('account.analytic.group', 'Analytic Group'),
            }

class account_analytic_line(osv.Model):

    _inherit = 'account.analytic.line'

    _columns = {
        'analytics_id': fields.many2one('account.analytic.plan.instance', 'Analytic Distribution'),
        'partner_id': fields.many2one('res.partner', 'Partner', select=1, ondelete='restrict'),
        'tax_code_id': fields.many2one('account.tax.code', 'Tax Account', 
            help="The Account can either be a base tax code or a tax code account."),
        'analytic_group_id': fields.related('account_id', 'analytic_group_id',
            type='many2one', relation='account.analytic.group', string='Analytic Group',
            store=True, readonly=True),
    }

class account_move_line(osv.osv):

    _inherit = "account.move.line"

    def create_analytic_lines(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        ids = isinstance(ids, (int, long)) and [ids] or ids

        res = super(account_move_line, self).create_analytic_lines(cr, uid, ids,context=context)

        analytic_line_obj = self.pool.get('account.analytic.line')
        for move_line in self.browse(cr, uid, ids, context=context):
           if move_line.analytics_id:
               for line in move_line.analytic_lines:
                   analytic_line_obj.write(cr, uid, line.id, {
                       'partner_id': move_line.partner_id.id,
                       'analytics_id': move_line.analytics_id.id,
                       'tax_code_id': move_line.tax_code_id.id,
                       }, context=context)
        return res
