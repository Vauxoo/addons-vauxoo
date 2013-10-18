#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Julio Cesar Serna Hernandez(julio@vauxoo.com)
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


import time
from openerp.osv import fields, osv
from openerp import netsvc
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _


class account_voucher_tax_assigned(osv.TransientModel):
    
    _name = 'account.voucher.tax.assigned'
    
    _columns = {
        'tax_ids': fields.many2many('account.tax', 'voucher_assgined_tax_rel',
                                'wiz_id',
                                'tax_id',
                                'Taxes to Close'),
        'account_ids': fields.many2many('account.account', 'assigned_account_rel',
                                'wiz_id',
                                'account_id',
                                'Account to Close'),
        'period_id': fields.many2one('account.period', 'Period', required=True,
                                        help='Period of Entries to find'),
    }
    
    def action_account_assigned(self, cr, uid, ids, context=None):
        aml_obj = self.pool.get('account.move.line')
        acc_voucher_tax_sat_obj = self.pool.get('account.voucher.tax.sat')
        if context is None:
            context = {}
        
        for tax_assigned in self.browse(cr, uid, ids, context=context):
            acc_vocuher_tax_sat = acc_voucher_tax_sat_obj.browse(cr, uid,
                                            context.get('active_id', False))
            taxe_assigned = [taxes.id for taxes in tax_assigned.tax_ids]
            move_line_to_close = aml_obj.search(cr, uid, [
                        ('tax_id_secondary', 'in', taxe_assigned),
                        ('credit', '>', 0.0),
                        ('period_id', '=', tax_assigned.period_id.id)
                        ])
            acc_voucher_tax_sat_obj.write(cr, uid, acc_vocuher_tax_sat.id,
                {'aml_ids': [(4, move_id) for move_id in move_line_to_close]})
        return True
    