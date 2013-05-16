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
import time
from openerp.tools.translate import _

from openerp.osv import osv, fields


class mrp_bom(osv.Model):
    _inherit = 'mrp.bom'

    def check_uom(self, cr, uid, ids, context=None):
        for mrp_bom in self.browse(cr, uid, ids, context=context):
            if mrp_bom.product_uom and\
                mrp_bom.product_id.uom_id.category_id.id !=\
                    mrp_bom.product_uom.category_id.id:
                return False
        return True

    _constraints = [(check_uom, _(
        'No puedes agregar un UdM que pertenezca a otra categoría que la que\
        tiene la unidad de medida default del producto'), ["product_uom"])]
