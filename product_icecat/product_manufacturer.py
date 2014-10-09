# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2011 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                       Raimon Esteve <resteve@zikzakmedia.com>
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv


class product_product(osv.Model):
    _inherit = 'product.product'
    _columns = {
        'manufacturer_pname': fields.char('Manufacturer Product Name',
            size=128),
    }


class product_attribute(osv.Model):
    _inherit = 'product.manufacturer.attribute'

    _columns = {
        'name': fields.char('Attribute', size=128, required=True),
        'value': fields.char('Value', size=128),
        'icecat_category': fields.char('Icecat Category', size=64),
        'sequence': fields.integer('Sequence'),
    }

    _order = 'sequence, id'

    _defaults = {
        'sequence': lambda *a: 10,
    }
