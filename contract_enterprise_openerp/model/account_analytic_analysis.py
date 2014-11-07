# !/usr/bin/python
# -*- encoding: utf-8 -*-
# #############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
# ############## Credits  #####################################################
#    Coded by: Luis Escobar <luis@vauxoo.com>
#    Audited by: Nhomar Hernandez <nhomar@vauxoo.com>
# #############################################################################
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
# #############################################################################
import logging

from openerp.osv import osv, fields


_logger = logging.getLogger(__name__)


class warranty_oerp(osv.Model):
    _name = 'account.warranty_oerp'

    def _check_overlapping(self, cr, uid, ids, context=None):
        obj_warranty = self.browse(cr, uid, ids[0], context=context)
        if obj_warranty.end_date < obj_warranty.start_date:
            return False
        pids = self.search(cr, uid,
                           [('end_date', '>=', obj_warranty.start_date),
                            ('start_date', '<=', obj_warranty.end_date),
                            ('contract_id', '=', obj_warranty.contract_id.id),
                            ('id', '<>', obj_warranty.id), ])
        if len(pids) > 0:
            return False
        return True

    def _check_duplicity(self, cr, uid, ids, context=None):
        obj_warranty = self.browse(cr, uid, ids[0], context=context)
        pids = self.search(
            cr,
            uid,
            [('enterprise_key', '=', obj_warranty.enterprise_key),
             ('id', '<>', obj_warranty.id)])
        if len(pids) > 0:
            return False
        return True

    _columns = {
        'start_date': fields.date('Start Date', help="""day when this contract
            was enabled by OpenERP and is shown in the contract PDF
            attached."""),
        'end_date': fields.date('End date', help="""day when this contract will
            end  by OpenERP and is shown in the contract PDF attached."""),
        'enterprise_key': fields.char(
            'Enterprise Contract Key',
            64,
            help="""Key given by OpenERP i.e: twa-1234355352ff"""),
        'contract_id': fields.many2one('account.analytic.account', 'Contract',
                                       help='Contract linked to warranty'),
    }
    _constraints = [
        (_check_overlapping, """Error!\n Date is/are invalid.""",
                   ['end_date']),
        (_check_duplicity, """Error!\n Enterprise Key exists in other
             contract.""", ['enterprise_key']),
    ]


class account_analytic_account(osv.Model):
    _inherit = 'account.analytic.account'
    _columns = {
        'license_oerp': fields.boolean(
            'This contract has Enterprise License',
            help='This check enables the management of warranties'),
        'warranty_oerp_ids': fields.one2many(
            'account.warranty_oerp',
            'contract_id', 'Warranties Enterprise',
            help="""List of Warranties Enterprise"""),
    }
