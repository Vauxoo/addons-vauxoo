# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from openerp import models, api, fields, _
from openerp.exceptions import Warning as UserError
import openerp.addons.decimal_precision as dp


class MrpProductProduct(models.TransientModel):
    _inherit = "mrp.product.produce"

    @api.cr_uid_context
    def on_change_qty(self, cr, uid, ids, product_qty, consume_lines,
                      context=None):
        """
        When changing the quantity of products to be produced it will
        recalculate the number of raw materials needed according
        to the scheduled products and the already consumed/produced products
        It will return the consume lines needed for the products to be produced
        which the user can still adapt
        """
        context = dict(context or {})
        res = super(MrpProductProduct, self). on_change_qty(cr, uid, ids,
                                                            product_qty,
                                                            consume_lines,
                                                            context=context)
        prod_obj = self.pool.get("mrp.production")
        production = prod_obj.browse(cr, uid, context['active_id'],
                                     context=context)
        if production.qty_available_to_produce < product_qty:
            raise UserError(_('''You cannot produce more than available to
                              produce for this order '''))

        return res

    @api.cr_uid_context
    def _get_product_qty(self, cr, uid, context=None):
        """ To obtain product quantity
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param context: A standard dictionary
        @return: Quantity
        """
        if context is None:
            context = {}
        res = super(MrpProductProduct, self)._get_product_qty(cr, uid,
                                                              context=context)
        prod = self.pool.get('mrp.production').browse(cr, uid,
                                                      context['active_id'],
                                                      context=context)
        return res > 0 and prod.qty_available_to_produce

    product_qty = fields.Float('Select Quantity',
                               default=_get_product_qty,
                               digits_compute=dp.
                               get_precision('Product Unit of Measure'),
                               required=True)

    @api.multi
    def do_produce(self):
        '''
        Overwritten to show a message if someone try to produce more than
        available to produce
        '''
        production_id = self._context.get('active_id', False)
        assert production_id, "Production Id should be specified "\
            "in context as a Active ID."
        production_brw = self.env['mrp.production'].browse(production_id)
        for record in self:
            if record.product_qty > production_brw.qty_available_to_produce:
                raise UserError(_('''You cannot produce more than available to
                                    produce for this order '''))

        return super(MrpProductProduct, self).do_produce()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
