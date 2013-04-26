# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: moylop260 (moylop260@vauxoo.com)
#              Isaac Lopez (isaac@vauxoo.com)
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

import time
import openerp.netsvc as netsvc
from openerp.osv import osv, fields
from mx import DateTime
from tools import config
from openerp.tools.translate import _


class purchase_order(osv.Model):
    _inherit = "purchase.order"

    def wkf_confirm_order(self, cr, uid, ids, context=None):
        product_supp_obj = self.pool.get('product.supplierinfo')
        company_id = self.pool.get(
            'res.users').browse(cr, uid, uid).company_id.id
        product_obj = self.pool.get('product.template')
        if super(purchase_order, self).wkf_confirm_order(cr, uid, ids,
                                                         context=context):
            for po in self.browse(cr, uid, ids, context=context):
                partner_id = po.partner_id.id
                for line in po.order_line:
                    product_id = line.product_id.product_tmpl_id.id
                    if not product_supp_obj.search(cr, uid,
                                                   [('product_id', '=',
                                                                   product_id),
                                                   ('name', '=', partner_id)]):
                        product_obj.write(cr, uid, [product_id],
                                          {
                                          'seller_ids': [(0, 0,
                                                          {'name': partner_id,
                                                           'min_qty': 1.0,
                                                           'delay': 1,
                                                           'sequence': 10,
                                                           'product_id':
                                                           product_id,
                                                           'company_id':
                                                           company_id,
                                                           'product_uom':
                                                           line and
                                                         line.product_id and
                                                         line.product_id.
                                                           uom_id and
                                                         line.product_id.
                                                           uom_id.id})]})
            return True
        else:
            return False
