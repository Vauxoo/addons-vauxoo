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

from openerp.osv import osv, fields
from openerp.tools.translate import _
import time


class stock_picking(osv.Model):
    _inherit = 'stock.picking'
    _columns = {
        'date_contract_expiry': fields.date(
            'Expiration of Contract Date',
            help='Expiration of Contract Date'),
    }

    def action_process(self, cur, uid, ids, context=None):
        """
        overwrite the method to add a verification of the contract Expiration
        date before process the stock picking.
        """
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        cr_date = time.strftime('%Y-%m-%d')
        sp_brw = self.browse(cur, uid, ids[0], context=context)
        if ((not sp_brw.date_contract_expiry) or
                (sp_brw.date_contract_expiry and cr_date <= sp_brw.date_contract_expiry) or
                context.get('force_expiry_pickings', False)):
            res = super(stock_picking, self).action_process(
                cur, uid, [sp_brw.id], context=context)
        else:
            raise osv.except_osv(_('Invalid Procedure'),
                _('The Contract Expiration Date already pass. You cannot'
                  ' process the stock picking.'))
        return res

    def copy(self, cur, uid, id, default=None, context=None):
        """
        Ovwerwrite the copy method to also copy the date_contract_expiry value.
        """
        default = default or {}
        context = context or {}
        picking_brw = self.browse(cur, uid, id, context=context)
        default['date_contract_expiry'] = False
        res = super(stock_picking, self).copy(
            cur, uid, id, default=default, context=context)
        return res


class stock_picking_in(osv.Model):
    _inherit = 'stock.picking.in'
    _columns = {
        'date_contract_expiry': fields.date(
            'Expiration of Contract Date',
            help='Expiration of Contract Date'),
    }

    def action_process(self, cur, uid, ids, context=None):
        """
        overwrite the method to add a verification of the contract Expiration
        date before process the stock picking in.
        """
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        cr_date = time.strftime('%Y-%m-%d')
        sp_brw = self.browse(cur, uid, ids[0], context=context)
        if ((not sp_brw.date_contract_expiry) or
                (sp_brw.date_contract_expiry and cr_date <= sp_brw.date_contract_expiry) or
                context.get('force_expiry_pickings', False)):
            res = super(stock_picking_in, self).action_process(
                cur, uid, [sp_brw.id], context=context)
        else:
            raise osv.except_osv(_('Invalid Procedure'),
                _('The Contract Expiration Date already pass. You cannot'
                  ' process the stock picking in.'))
        return res

    def copy(self, cur, uid, id, default=None, context=None):
        """
        Ovwerwrite the copy method to also copy the date_contract_expiry value.
        """
        default = default or {}
        context = context or {}
        picking_brw = self.browse(cur, uid, id, context=context)
        default['date_contract_expiry'] = False
        res = super(stock_picking_in, self).copy(
            cur, uid, id, default=default, context=context)
        return res


class stock_picking_out(osv.Model):
    _inherit = 'stock.picking.out'
    _columns = {
        'date_contract_expiry': fields.date(
            'Expiration of Contract Date',
            help='Expiration of Contract Date'),
    }

    def action_process(self, cur, uid, ids, context=None):
        """
        overwrite the method to add a verification of the contract Expiration
        date before process the stock picking out.
        """
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        cr_date = time.strftime('%Y-%m-%d')
        sp_brw = self.browse(cur, uid, ids[0], context=context)
        if ((not sp_brw.date_contract_expiry) or
                (sp_brw.date_contract_expiry and cr_date <= sp_brw.date_contract_expiry) or
                context.get('force_expiry_pickings', False)):
            res = super(stock_picking_out, self).action_process(
                cur, uid, [sp_brw.id], context=context)
        else:
            raise osv.except_osv(_('Invalid Procedure'),
                _('The Contract Expiration Date already pass. You cannot'
                  ' process the stock picking out.'))
        return res

    def copy(self, cur, uid, id, default=None, context=None):
        """
        Ovwerwrite the copy method to also copy the date_contract_expiry value.
        """
        default = default or {}
        context = context or {}
        picking_brw = self.browse(cur, uid, id, context=context)
        default['date_contract_expiry'] = False
        res = super(stock_picking_out, self).copy(
            cur, uid, id, default=default, context=context)
        return res
