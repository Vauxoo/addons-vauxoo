# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: Jose Morales <jose@vauxoo.com>
#    Planned by: Nhomar Hernandez <nhomar@vauxoo.com>
#    Audited by: Jose Morales <jose@vauxoo.com>
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
from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError


class MrpProduction(models.Model):

    _inherit = 'mrp.production'

    @api.multi
    def _compute_qty_to_produce(self):
        '''
        Used to shown the quantity available to produce considering the
        reserves in the moves related
        '''
        for record in self:
            total = record.get_qty_available_to_produce()
            record.qty_available_to_produce = total

    qty_available_to_produce = fields.Float(
        string='Quantity Available to Produce',
        compute='_compute_qty_to_produce', readonly=True,
        help='Quantity available to produce considering '
        'the quantities reserved by the order')

    @api.multi
    def test_ready(self):
        res = super(MrpProduction, self).test_ready()
        for record in self:
            if record.qty_available_to_produce > 0:
                res = True
            else:
                res = False
        return res

    @api.multi
    def get_qty_available_to_produce(self):
        '''
        Compute the total available to produce considering
        the lines reserved
        '''
        uom_obj = self.env['product.uom']
        for record in self:
            bom_obj = self.env['mrp.bom']
            if not record.move_lines.mapped('reserved_quant_ids'):
                return 0.0
            self._cr.execute('''
                             SELECT m.product_id,
                                    sum(q.qty) AS total
                             FROM stock_move AS m
                             LEFT OUTER JOIN stock_quant AS q ON
                                             q.reservation_id=m.id
                             WHERE m.raw_material_production_id = {prod_id}
                             GROUP BY m.product_id;
                             '''.format(prod_id=record.id))
            result = {i.get('product_id'): i.get('total') or 0
                      for i in self._cr.dictfetchall()}
            product_uom_qty = uom_obj._compute_qty(record.product_uom.id,
                                                   1,
                                                   record.product_id.uom_id.id)
            consume_lines = bom_obj._bom_explode(record.bom_id,
                                                 record.product_id,
                                                 product_uom_qty)

            qty = []
            for line in consume_lines and consume_lines[0] or ():
                product_id = line.get('product_id')
                val = line.get('product_qty') and \
                    int(result.get(product_id, 0) /
                        line.get('product_qty')) or 0
                qty.append(val)

        return min(qty)

    @api.cr_uid_id_context
    def action_produce(self, cr, uid, production_id, production_qty,
                       production_mode,
                       wiz=False, context=None):
        '''
        Overwritten the method to avoid produce more than available to produce
        @param production_id: the ID of mrp.production object
        @param production_qty: specify qty to produce in the uom of the
        production order
        @param production_mode: specify production mode
        (consume/consume&produce).
        @param wiz: the mrp produce product wizard, which will tell the amount
        of consumed products needed
        @return: True
        '''
        record = self.browse(cr, uid, production_id)
        if production_qty > record.qty_available_to_produce:
            raise UserError(_('''You cannot produce more than available to
                                produce for this order '''))
        return super(MrpProduction, self).action_produce(cr, uid,
                                                         production_id,
                                                         production_qty,
                                                         production_mode,
                                                         wiz=wiz,
                                                         context=context)
