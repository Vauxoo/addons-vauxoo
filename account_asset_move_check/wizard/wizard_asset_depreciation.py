# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2015 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Luis Torres (luis_t@vauxoo.com)
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

from openerp.osv import fields, osv


class wizard_asset_depreciation(osv.osv_memory):
    _name = 'wizard.asset.depreciation'

    _columns = {
        'period_id': fields.many2one(
            'account.period', 'Period', help='Select period to moves'
            'that will write ckeck post = True', required=True),
    }

    def _get_period(self, cr, uid, context=None):
        periods = self.pool.get('account.period').find(
            cr, uid, context=context)
        if periods:
            return periods[0]
        return False

    _defaults = {
        'period_id': _get_period,
    }

    def _write_check_post(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        acc_asset_obj = self.pool.get('account.asset.asste')
        data = self.browse(cr, uid, ids, context=context)[0]
        print 'data', data.period_id
        for asset in acc_asset_obj.browse(
                cr, uid, context.get('active_ids', [])):
            print asset
        return True
