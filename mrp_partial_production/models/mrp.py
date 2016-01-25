# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: Jose Suniaga <josemiguel@vauxoo.com>
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
        for record in self:
            total = record.get_qty_available_to_produce()
            record.qty_available_to_produce = total

    @api.multi
    @api.depends('move_lines.reserved_quant_ids')
    def _moves_assigned(self):
        """ Test whether all the consume lines are assigned """
        for production in self:
            if production.qty_available_to_produce > 0:
                production.ready_production = True
            else:
                production.ready_production = False

    qty_available_to_produce = fields.Float(
        string='Quantity Available to Produce',
        compute='_compute_qty_to_produce', readonly=True,
        help='Quantity available to produce considering '
        'the quantities reserved by the order')

    ready_production = fields.Boolean(compute='_moves_assigned',
                                      store=True)

    @api.multi
    def get_qty_available_to_produce(self):
        '''
        Compute the total available to produce considering
        the lines served
        '''
        uom_obj = self.env['product.uom']
        for record in self:
            total = 0
            done = 0.0
            if record.move_created_ids2:
                moves = record.move_created_ids2.\
                    filtered(lambda a: not a.scrapped)
                done = sum(moves.mapped('product_uom_qty'))
            if not record.move_lines.mapped('reserved_quant_ids'):
                return total
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
            incomplete = False
            for total in range(1, int((record.product_qty - done) + 1)):
                product_uom_qty = uom_obj.\
                    _compute_qty(record.product_uom.id,
                                 total,
                                 record.product_id.uom_id.id)
                consume_lines = record.\
                    _calculate_qty(record,
                                   product_qty=product_uom_qty)
                for line in consume_lines:
                    product_id = line.get('product_id')
                    if not line.get('product_qty') <= result.get(product_id):
                        total -= 1
                        incomplete = True
                        break
                if incomplete:
                    break
        return total

    @api.cr_uid_id_context
    def action_produce(self, cr, uid, production_id, production_qty,
                       production_mode,
                       wiz=False, context=None):
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
