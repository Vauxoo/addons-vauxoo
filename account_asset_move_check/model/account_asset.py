# -*- coding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: Sabrina Romero (sabrina@vauxoo.com)
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
import openerp.addons.decimal_precision as dp


class AccountAssetDepreciationLine(osv.Model):
    _inherit = 'account.asset.depreciation.line'

    def _get_move_check(self, cr, uid, ids, name, args, context=None):
        res = super(AccountAssetDepreciationLine, self)._get_move_check(
            cr, uid, ids, name, args, context=context)
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = bool(line.move_id or line.historical)
        return res

    _columns = {
        'historical': fields.boolean('Historical'),
        'move_check': fields.function(
            _get_move_check, method=True, type='boolean', string='Posted',
            store=True),
    }

    _defaults = {
        'historical': False,
    }


class AccountAssetAsset(osv.osv):
    _inherit = 'account.asset.asset'

    def _amount_residual(self, cr, uid, ids, name, args, context=None):
        res = super(AccountAssetAsset, self)._amount_residual(
            cr, uid, ids, name, args, context=context)
        dep_line_obj = self.pool.get('account.asset.depreciation.line')
        for asset in res:
            dep_lines = dep_line_obj.search(
                cr, uid, [('asset_id', '=', asset),
                          ('move_id', '=', False),
                          ('move_check', '=', True),
                          ], context=context)
            amount = 0
            for line in dep_line_obj.browse(
                    cr, uid, dep_lines, context=context):
                amount += line.amount or 0.0
            res.update({asset: res.get(asset, 0.0) - amount})
        return res

    _columns = {
        'value_residual': fields.function(
            _amount_residual, method=True,
            digits_compute=dp.get_precision('Account'),
            string='Net Book Value'),
    }
