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

from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
from openerp import tools

class res_partner(osv.Model):

    _inherit = 'res.partner'
    _columns = {
        'product_ids': fields.many2many(
            'product.product',
            'partner_product_rel',
            'partner_id', 'product_id',
            'Products',
            help='Supplier List of Offered Products'),
    }

    def copy(self, cur, uid, id, default=None, context=None):
        """
        overwrite the copy orm method to clean the produc_ids list.
        """
        context = context or {}
        default = default or {}
        default.update({'product_ids': []})
        return super(res_partner, self).copy(
            cur, uid, id, default=default, context=context)
