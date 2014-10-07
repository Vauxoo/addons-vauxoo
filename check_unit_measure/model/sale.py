# -*- encoding: utf-8 -*-
##############################################################################
# Copyright (c) 2011 OpenERP Venezuela (http://openerp.com.ve)
# All Rights Reserved.
# Programmed by: Israel Fermín Montilla  <israel@openerp.com.ve>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
###############################################################################
from openerp.osv import osv
from openerp.tools.translate import _


class inherits_sale(osv.Model):

    '''Inherit sale orde line  model to add constraint and avoid add a prodct
    with a diferent unit measure'''

    _inherit = 'sale.order.line'

    def _check_unit_measure(self, cr, uid, ids, context=None):
        print 'sale check'
        sol_brw = self.browse(cr, uid, ids[0], context=context)
        if sol_brw.product_id and not\
                sol_brw.product_id.uom_id.id == sol_brw.product_uom.id:
            raise osv.except_osv(_('Error !'), _(
                "The Unit measure in the line will be the unit measure\
                for this product %s .") % (sol_brw.product_id.name,))
        return True

    _constraints = [
        (_check_unit_measure, 'Error!\nThe Unit measure in the line\
        will be the unit measure for this product.', [
         'product_uom'])
    ]

    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
                          uom=False, qty_uos=0, uos=False, name='',
                          partner_id=False, lang=False, update_tax=True,
                          date_order=False, packaging=False,
                          fiscal_position=False, flag=False, context=None):
        context = context or {}
        product_obj = self.pool.get('product.product')
        res = super(
            inherits_sale, self).product_id_change(cr, uid, ids, pricelist,
                   product, qty=qty,
                   uom=uom, qty_uos=qty_uos, uos=uos, name=name,
                   partner_id=partner_id, lang=lang, update_tax=update_tax,
                   date_order=date_order, packaging=packaging,
                   fiscal_position=fiscal_position, flag=flag, context=context)
        uom_id = product and product_obj.browse(cr, uid, product, context)
        uom_id = uom_id and uom_id.uom_id and uom_id.uom_id.id
        res.get('value', False) and res.get(
            'value', {}).update({'product_uom': uom_id})
        return res
