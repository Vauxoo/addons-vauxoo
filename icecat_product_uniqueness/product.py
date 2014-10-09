# -*- encoding: utf-8 -*-
##############################################################################
# Copyright (c) 2011 OpenERP Venezuela (http://openerp.com.ve)
# All Rights Reserved.
# Programmed by: Israel Fermín Montilla  <israel@openerp.com.ve>
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
###############################################################################
from openerp.osv import osv


class product_inherited(osv.Model):
    """
    Checks if a loaded product already exists on the database
    """
    _inherit = 'product.product'

    def _find_product(self, ean13, products):
        for p in products:
            if ean13 == p.ean13:
                return p
        return None

    def _check_uniqueness(self, cr, uid, ids, context=None):
        all_ids = self.search(cr, uid, [('id', '<>', ids[0])])
        all_products = [p for p in self.browse(
            cr, uid, all_ids, [], context) if p.ean13 != False]
        if all_products == []:
            return True
        for product in self.browse(cr, uid, ids, context):
            if product.ean13 == False:
                return True
            if product.ean13 in [p.ean13 for p in all_products]:
                p = self._find_product(product.ean13, all_products)
                if p.company_id.name == product.company_id.name:
                    return False
        return True

    _constraints = [(
        _check_uniqueness, 'ERROR, product already exists for this company',
            ['ean13'])]
