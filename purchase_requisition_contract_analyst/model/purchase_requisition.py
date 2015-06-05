# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
############# Credits #########################################################
#    Coded by: Katherine Zaoral <kathy@vauxoo.com
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


class purchase_requisition(osv.Model):

    _inherit = 'purchase.requisition'
    _columns = {
        'purchaser_id': fields.many2one(
            'res.users',
            'P&C Analyst',
            domain=[('is_purchaser', '=', True)],
            help=('Contract Analyst responsible to evaluate the current'
                  ' purchase requisition.')),
    }

    def copy(self, cr, uid, id, default=None, context=None):
        default = default or {}
        default.update({'purchaser_id': False})
        return super(purchase_requisition, self).copy(cr, uid, id, default,
                                                      context=context)


class res_partner(osv.Model):

    _inherit = 'res.partner'
    _columns = {
        'is_purchaser': fields.boolean(
            'P&C Analyst',
            help='Is this a Purchaser?'),
    }

    def copy(self, cr, uid, id, default=None, context=None):
        default = default or {}
        default.update({'is_purchaser': False})
        return super(res_partner, self).copy(cr, uid, id, default,
                                             context=context)
