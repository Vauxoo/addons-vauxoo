#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: Juan Carlos Funes(juan@vauxoo.com)
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
##########################################################################

import threading
import pooler
import openerp.netsvc as netsvc
import os
from openerp.osv import osv, fields


class procurement_compute_all(osv.TransientModel):
    _inherit = 'procurement.order.compute.all'

    _columns = {
        'product_ids': fields.many2many('product.product',
            'procurement_product_rel', 'procurement_id',
            'product_id', 'Products')
    }

    def procure_calculation(self, cr, uid, ids, context=None):
        form = self.read(cr, uid, ids, [])
        products = form and form[0]['product_ids'] or False
        context.update({'product_ids': products})
        res = super(procurement_compute_all, self).procure_calculation(
            cr, uid, ids, context=context)
        return res


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
