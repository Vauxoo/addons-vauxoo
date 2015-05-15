# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
###############################################################################
#    Credits:
#    Coded by: Katherine Zaoral <kathy@vauxoo.com>
#    Planified by: Nhomar Hernandez <nhomar@vauxoo.com>
#    Audited by: Nhomar Hernandez <nhomar@vauxoo.com>
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

from openerp import models, api
from openerp.tools.translate import _
from openerp.exceptions import Warning


class PurchaseOrderLine(models.Model):

    _inherit = 'purchase.order.line'

    @api.v7
    def onchange_product_id(
            self, cr, uid, ids, pricelist, product, qty, uom,
            partner_id, date_order=False, fiscal_position_id=False,
            date_planned=False, name=False, price_unit=False, state='draft',
            context=None):
        """
        Raise a exception is you select discontinued product.
        """
        context = context or {}
        product_obj = self.pool.get('product.template')
        if product:
            product_brw = product_obj.browse(cr, uid, product, context=context)
            if product_brw.state in ['obsolete']:
                replacements = [
                    item.name for item in product_brw.replacement_product_ids]
                msg = (_('This product you select is discontinued product. '
                         'Select one of the replacement products') + ':\n'
                       + str(replacements))
                raise Warning(msg)

        res = super(PurchaseOrderLine, self).onchange_product_id(
            cr, uid, ids, pricelist, product, qty, uom,
            partner_id, date_order=date_order,
            fiscal_position_id=fiscal_position_id, date_planned=date_planned,
            name=name, price_unit=price_unit, state=state, context=context)
        return res
