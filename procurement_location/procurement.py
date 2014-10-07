# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
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
from openerp.osv import osv


class procurement_order(osv.Model):
    _inherit = 'procurement.order'

    def make_mo(self, cr, uid, ids, context=None):
        res = super(procurement_order, self).make_mo(
            cr, uid, ids, context=context)
        mrp_prod_obj = self.pool.get('mrp.production')
        cat_prod = self.browse(
            cr, uid, ids, context=context)[0].product_id.categ_id
        loc_src = cat_prod.location_src_id and\
            cat_prod.location_src_id.id or False
        loc_dest = cat_prod.location_dest_id and\
            cat_prod.location_dest_id.id or False
        if loc_src:
            mrp_prod_obj.write(cr, uid, res.values()[
                               0], {'location_src_id': loc_src})
        if loc_dest:
            mrp_prod_obj.write(cr, uid, res.values()[
                               0], {'location_dest_id': loc_dest})
        return res
