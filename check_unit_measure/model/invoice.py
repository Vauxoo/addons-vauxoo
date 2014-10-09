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


class inherit_account_invocie_line(osv.Model):

    '''Inherit account.invoice.line to set unit measure for product in the line'''

    _inherit = 'account.invoice.line'

    def _check_unit_measure(self, cr, uid, ids, context=None):
        ail_brw = self.browse(cr, uid, ids[0], context=context)
        if ail_brw.invoice_id.type == 'out_invoice':
            if not ail_brw.product_id and\
                ail_brw.product_id.uom_id.id == ail_brw.uos_id and\
                    ail_brw.uos_id.id:
                raise osv.except_osv(_('Error !'), _(
                    "The Unit measure in the line will be the unit measure set\
                    on the product configuration to sale %s .") %
                    (ail_brw.product_id.name,))

        if ail_brw.invoice_id.type == 'in_invoice':
            if not ail_brw.product_id and\
                ail_brw.product_id.uom_po_id.id == ail_brw.uos_id and\
                    ail_brw.uos_id.id:
                raise osv.except_osv(_('Error !'), _(
                    "The Unit measure in the line will be the unit measure set\
                    on the product configuration to purchase %s .") %
                    (ail_brw.product_id.name,))
        return True

    _constraints = [
        (_check_unit_measure,
         'Error!\nThe Unit measure in the line will be the unit measure\
         for this product.', ['uos_id'])
    ]
