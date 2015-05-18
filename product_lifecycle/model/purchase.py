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

from openerp import models, fields, api
from openerp.tools.translate import _


class PurchaseOrderLine(models.Model):

    _inherit = 'purchase.order.line'

    replacement_product_id = fields.Many2one(
        'product.product', string='Replacement',
        help='When the Product you select is a discontinued Product will'
             ' enable this field so you can choose the replacement you want')
    discontinued = fields.Boolean('Discontinued')

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
        product_obj = self.pool.get('product.product')
        res = super(PurchaseOrderLine, self).onchange_product_id(
            cr, uid, ids, pricelist, product, qty, uom,
            partner_id, date_order=date_order,
            fiscal_position_id=fiscal_position_id, date_planned=date_planned,
            name=name, price_unit=price_unit, state=state, context=context)
        res.get('domain', dict()).update({
            'replacement_product_id': [('id', 'in', [])]})
        res.get('value').update({'discontinued': False})

        if product:
            product_brw = product_obj.browse(cr, uid, product, context=context)
            if product_brw.state in ['obsolete']:
                product_tmpls = [
                    item.id for item in product_brw.replacement_product_ids]
                replacements = product_obj.search(
                    cr, uid, [('product_tmpl_id', 'in', product_tmpls)],
                    context=context)
                msg = (product_brw.name + " " + _('is a discontinued product.')
                       + '\n')
                if replacements:
                    msg += _('Select one of the replacement products.')
                else:
                    msg += ('\n'*2 + _(
                        'The are not replacement products defined for the'
                        ' product you selected. Please select another product'
                        ' or define a replacement product in the product form'
                        ' view.'))
                res.update({'warning': {'title': 'Error!', 'message': msg}})
                res.get('domain').update({
                    'replacement_product_id': [('id', 'in', replacements)]})
                res.get('value').update({'discontinued': True})
        return res

    @api.onchange('replacement_product_id')
    def onchange_replacement_product_id(self):
        """
        Write the replacement product over the product field.
        """
        self.product_id = self.replacement_product_id
        self.replacement_product_id = False
