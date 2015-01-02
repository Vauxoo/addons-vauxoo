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


class account_asset_depreciation_line(osv.Model):
    _inherit = 'account.asset.depreciation.line'

    def _get_move_check(self, cr, uid, ids, name, args, context=None):
        res = super(account_asset_depreciation_line, self)._get_move_check(
            cr, uid, ids, name, args, context=context)
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = bool(line.move_id or line.check_posted)
        return res

    _columns = {
        'check_posted': fields.boolean('Check Posted'),
        'move_check': fields.function(
            _get_move_check, method=True, type='boolean', string='Posted',
            store=True)
    }

    _defaults = {
        'check_posted': False,
    }
