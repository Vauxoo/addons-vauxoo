# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Vauxoo C.A. (http://openerp.com.ve/) All Rights Reserved.
#                    Humberto Arocha <hbto@vauxoo.com>
#
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
from openerp.osv import osv


class analytic_default(osv.osv):
    _inherit = "account.analytic.default"

    def _check_analytics_double(self, cr, uid, ids, context=None):
        for ad_brw in self.browse(cr, uid, ids, context=context):
            if all([ad_brw.analytic_id, ad_brw.analytics_id]):
                return False
        return True

    def _check_analytics_missing(self, cr, uid, ids, context=None):
        for ad_brw in self.browse(cr, uid, ids, context=context):
            if not any([ad_brw.analytic_id, ad_brw.analytics_id]):
                return False
        return True

    _constraints = [
        (_check_analytics_double,
         '\nYou cannot create an Analytic Default with both '
         '\nAnalytic Distribution and Analytic Accounts. '
         '\nYou can only use one of them.',
         ['analytic_id', 'analytics_id']),
        (_check_analytics_missing,
         '\nYou cannot create an Analytic Default with neither '
         '\nAnalytic Distribution nor Analytic Accounts. '
         '\nYou have to use at least one of them.',
         ['analytic_id', 'analytics_id']),
    ]
