# coding: utf-8
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (http://www.vauxoo.com).
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


class ProductProduct(osv.Model):

    """To add two fields which determine if a product is show in restaurant and/or delivery
    point of sale
    """
    _inherit = 'product.product'
    _description = ('')
    _columns = {
        'restaurant': fields.boolean('POS Restaurant', help='To be sold in restaurant'),
        'delivery': fields.boolean('POS Delivery', help='To be sold in delivery'),
    }
