# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
# Credits #####################################################################
#    Coded by: Yanina Aular <yanina.aular@vauxoo.com>
#    Planified by: Humberto Arocha <hbto@vauxoo.com>
#    Audited by: Humberto Arocha <hbto@vauxoo.com>
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

from openerp.osv import osv
from openerp.tools.translate import _


class stock_partial_picking(osv.osv_memory):
    _inherit = "stock.partial.picking"

    def do_partial(self, cr, uid, ids, context=None):
        context = dict(context or {})
        assert len(ids) == 1, ('Partial picking processing may only be done '
                               'one at a time.')
        uom_obj = self.pool.get('product.uom')
        # rc_obj = self.pool.get('res.company')
        partial = self.browse(cr, uid, ids[0], context=context)

        fnc_super = super(stock_partial_picking, self).do_partial
        # TODO: Write method and fields in company to provide this feature
        # if not rc_obj.check_fulfillment(cr, uid, uid, context=context):
        #     return fnc_super(cr, uid, ids, context=context)

        for wizard_line in partial.move_ids:
            sm_brw = wizard_line.move_id

            # Quantiny must be Positive
            if wizard_line.quantity < 0:
                raise osv.except_osv(_('Warning!'),
                                     _('Please provide proper Quantity.'))

            # If line was newly created on wizard Shall we allow that?
            # TODO: We shall set a condition somewhere
            if not sm_brw:
                continue

            # Check if this line is coming from a purchase_line_id
            if not sm_brw.purchase_line_id:
                continue
            pol_brw = sm_brw.purchase_line_id
            pol_uom_id = pol_brw.product_uom
            src = wizard_line.location_id.usage
            dst = wizard_line.location_dest_id.usage
            line_uom = wizard_line.product_uom
            qty = 0.0
            if src == dst:
                continue
            elif dst == 'internal':
                qty = uom_obj._compute_qty_obj(cr, uid, line_uom,
                                               wizard_line.quantity,
                                               pol_uom_id,
                                               context=context)
            elif src == 'internal':
                qty = -uom_obj._compute_qty_obj(cr, uid, line_uom,
                                                wizard_line.quantity,
                                                pol_uom_id,
                                                context=context)
            excess = pol_brw.qty_delivered + qty - pol_brw.product_qty > 0
            defect = pol_brw.qty_delivered + qty < 0
            if excess:
                # TODO: Add a more detailed Explanation
                raise osv.except_osv(
                    _('Excess Detected!'),
                    _('You can not receive more than ordered'))
            if defect:
                # TODO: Add a more detailed Explanation
                raise osv.except_osv(
                    _('Defect Detected!'),
                    _('You can not return more than received'))
        return fnc_super(cr, uid, ids, context=context)
