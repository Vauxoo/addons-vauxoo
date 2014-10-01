# -*- encoding: utf-8 -*-
#
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#
#    Coded by: jorge_nr (jorge_nr@vauxoo.com)
#
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
#

from openerp.osv import osv
from openerp.tools.translate import _


class res_partner(osv.Model):
    _inherit = 'res.partner'

    def _check_vat_uniqueness(self, cr, uid, ids, context=None):
        """ Check that the vat is unique in the level 
            where the partner in the tree
        """
        if context is None:
            context = {}

        user_company = self.pool.get(
            'res.users').browse(cr, uid, uid).company_id

        # User must be of MX
        if not (user_company.partner_id and\
            user_company.partner_id.country_id\
            and user_company.partner_id.country_id.code == 'MX'):
            return True

        partner_brw = self.browse(cr, uid, ids)
        current_vat = partner_brw[0].vat
        current_parent_id = partner_brw[0].parent_id

        if not current_vat:
            return True  # Accept empty VAT's

        # Partners without parent, must have VAT uniqueness
        if not current_parent_id:
            duplicates = self.browse(cr, uid, self.search(
                cr, uid, [('vat', '=', current_vat),
                    ('parent_id', '=', None),
                    ('id', '!=', partner_brw[0].id)]))
            return not duplicates

        return True

    _constraints = [
        (_check_vat_uniqueness,
         _("Error ! Partner's VAT must be a unique value or empty"), 
         []), ]
