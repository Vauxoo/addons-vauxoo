#!/usr/bin/python
# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
############# Credits #########################################################
#    Coded by: Yanina Aular <yanina.aular@vauxoo.com
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


class purchase_order(osv.Model):

    _inherit = 'purchase.order'
    _columns = {
        'purchaser_id': fields.many2one(
            'res.users',
            'P&C Analyst',
            domain=[('is_purchaser', '=', True)],
            help=('Contract Analyst responsible to evaluate the current'
                  ' purchase order.')),
    }
    _defaults = {
        'purchaser_id': lambda s, c, u, ctx: u,
            }

class purchase_requisition(osv.Model):

    _inherit = 'purchase.requisition'

    def make_purchase_order(self, cr, uid, ids, partner_id,
                            context=None):
        if context is None:
            context = {}
        res = super(purchase_requisition, self).make_purchase_order(cr, uid, ids, partner_id, context=context)

        po_obj = self.pool.get('purchase.order')
        for requisition in self.browse(cr, uid, ids, context=context):
            po_req = po_obj.search(cr, uid, [('requisition_id', '=', requisition.id)], context=context)
            for po_id in po_req:
                po_obj.write(cr, uid, [po_id], {'purchaser_id': requisition.purchaser_id}, context=context)
        return res
