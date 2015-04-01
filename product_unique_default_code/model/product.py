# -*- coding: utf-8 -*-
# ##########################################################################
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
from openerp import _, api
from openerp.exceptions import except_orm


class ProductTemplate(osv.Model):
    _inherit = "product.template"

    @api.onchange('default_code')
    def unique_default_code(self):
        """Check if any product already have the given default code.

        :raise orm.except_orm: if the default code is not unique.
        """
        if self.search([('default_code', 'like', self.default_code)]):
            raise except_orm(
                _('Error!'),
                _(
                    'Internal code "{}" is already set to another product!.'
                    ' Please, set another Internal code to move forward.'
                )
            )


class ProductProduct(osv.Model):
    _inherit = "product.product"

    @api.one
    def copy(self, default=None):

        if not default:
            default = {}

        default['default_code'] = (
            self.default_code
            and self.default_code + ' (copy)'
            or False
        )

        return super(ProductProduct, self).copy(default=default)
