# -*- coding: utf-8 -*-
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


class Product(osv.Model):
    _inherit = "product.product"

    def copy(self, cr, uid,
             id,  # pylint: disable=W0622
             default=None, context=None):
        """
        Set default_code equal to False if
        not is defined in default variable
        to allow duplicate record with unique constraint
        """
        if default is None:
            default = {}
        if 'default_code' not in default:
            default['default_code'] = False
        return super(Product, self).copy(
            cr, uid, id, default, context=context)

    _sql_constraints = [
        #  Add unique default_code constraint.
        #  Not is per company, because product
        #  can use "False" company_id for global product.
        #  Then this may cause has product with
        #  "default code" duplicated.
        ('default_code_unique', 'unique (default_code)',
         'The code of product must be unique !'),
    ]
