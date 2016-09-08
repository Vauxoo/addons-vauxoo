# coding: utf-8
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


class StockPartialPicking(osv.osv_memory):
    _inherit = "stock.partial.picking"

    def do_partial(self, cr, uid, ids, context=None):
        context = dict(context or {})
        assert len(ids) == 1, ('Partial picking processing may only be done '
                               'one at a time.')
        uom_obj = self.pool.get('product.uom')
        ru_obj = self.pool.get('res.users')
        sp_obj = self.pool.get('stock.picking')
        partial = self.browse(cr, uid, ids[0], context=context)
        picking_id = partial.picking_id.id

        fnc_super = super(StockPartialPicking, self).do_partial

        ru_brw = ru_obj.browse(cr, uid, uid, context=context)
        rc_brw = ru_brw.company_id
        if not rc_brw.check_purchase_fulfillment:
            return fnc_super(cr, uid, ids, context=context)

        do_raise = False
        msg_raise = ''
        for wizard_line in partial.move_ids:
            sm_brw = wizard_line.move_id
            line_uom = wizard_line.product_uom

            # Quantity must be Positive
            if wizard_line.quantity < 0:
                raise osv.except_osv(_('Warning!'),
                                     _('Please provide proper Quantity.'))

            # If line was newly created on wizard Shall we allow that?
            # TODO: We shall set a condition somewhere
            if not sm_brw:
                do_raise = True
                msg_raise += _(u'%(product)s is being received '
                               '[%(ordered)s %(wz_uom)s] and was created from '
                               'scratch.\n' % dict(
                                   product=wizard_line.name,
                                   ordered=wizard_line.quantity,
                                   wz_uom=line_uom.name,))
                continue

            # Check if this line is coming from a purchase_line_id
            if not sm_brw.purchase_line_id:
                continue
            pol_brw = sm_brw.purchase_line_id
            pol_uom_id = pol_brw.product_uom
            src = wizard_line.location_id.usage
            dst = wizard_line.location_dest_id.usage
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
                do_raise = True
                msg_raise += _(u'For %(product)s, it was ordered '
                               '[%(ordered)s %(uom)s]'
                               ' received [%(received)s %(uom)s] receiving '
                               '[%(receiving)s %(wz_uom)s].\n' % dict(
                                   product=sm_brw.name,
                                   ordered=pol_brw.product_qty,
                                   uom=pol_uom_id.name,
                                   received=pol_brw.qty_delivered,
                                   receiving=qty, wz_uom=line_uom.name,))
            if defect:
                do_raise = True
                msg_raise += _(u'For %(product)s, it was received '
                               '[%(received)s %(uom)s] returning '
                               '[%(receiving)s %(wz_uom)s].\n' % dict(
                                   product=sm_brw.name,
                                   uom=pol_uom_id.name,
                                   received=pol_brw.qty_delivered,
                                   receiving=qty,
                                   wz_uom=line_uom.name,
                               ))

        if ru_brw.skip_purchase_fulfillment:
            do_raise = False

        if do_raise:
            raise osv.except_osv(
                _('Excess / Defect Detected!'),
                msg_raise)

        res = fnc_super(cr, uid, ids, context=context)

        if 'res_id' in res:
            picking_id = res['res_id']

        # Message is to be sent when picking is done
        if msg_raise:
            sp_obj.message_post(
                cr, uid, picking_id,
                _('Excess / Defect Detected!'),
                msg_raise,
                subtype='mail.mt_comment',
                context=context)

        return res
