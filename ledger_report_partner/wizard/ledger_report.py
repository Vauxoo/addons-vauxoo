#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: Vauxoo C.A.
#    Planified by: Nhomar Hernandez
#    Audited by: Vauxoo C.A.
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
##########################################################################

from openerp.osv import osv, fields
import openerp.tools as tools
from openerp.tools.translate import _

from tools import config
import openerp.netsvc as netsvc
import decimal_precision as dp
import time


class ledger_report(osv.TransientModel):
    _inherit = "account.report.general.ledger"
    _name = "ledger.report"
    _columns = {
        'partner_id': fields.many2one('res.partner', 'Partner',
            help="Select the Partner"),
    }

    _defaults = {
        'initial_balance': True,
        'amount_currency': False,
    }

    def _print_report(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        data = self.pre_print_report(cr, uid, ids, data, context=context)
        data['form'].update(self.read(cr, uid, ids, [
                            'landscape',  'initial_balance',
                            'amount_currency', 'sortby', 'partner_id'])[0])
        if not data['form']['fiscalyear_id']:  # GTK client problem onchange does not consider in save record
            data['form'].update({'initial_balance': False})
        res = data['form']['partner_id'] and \
            ({ 'type': 'ir.actions.report.xml',
                'report_name': 'report.ledger', 'datas': data}) or \
            ({'type': 'ir.actions.report.xml', 'report_name':
              'report.ledger_partner_field', 'datas': data})
        print res
        return res
