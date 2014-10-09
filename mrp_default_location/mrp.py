# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: julio (julio@vauxoo.com)
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

from openerp.osv import osv


class mrp_production(osv.Model):
    _inherit = 'mrp.production'

    def product_id_change(self, cr, uid, ids, product_id, context=None):
        res = super(mrp_production, self).product_id_change(
            cr, uid, ids, product_id, context=context)
        if product_id:
            product = self.pool.get('product.product').browse(
                cr, uid, product_id, context=context)
            res['value'].update({
                'location_src_id': product.categ_id and
                                product.categ_id.location_src_id.id or False,
                'location_dest_id': product.categ_id and
                                product.categ_id.location_dest_id.id or False})
        else:
            res['value'].update({'location_src_id': False,
                                 'location_dest_id': False})
        return res
