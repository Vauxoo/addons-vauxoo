# coding: utf-8
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://www.vauxoo.com>).
#    All Rights Reserved
# ############ Credits ########################################################
#    Coded by: Katherine Zaoral <kathy@vauxoo.com>
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

from openerp.osv import osv, fields
from openerp.tools.translate import _


class PurchaseRequisition(osv.Model):

    _inherit = 'purchase.requisition'
    _columns = {
        'currency_id': fields.many2one(
            'res.currency', 'Currency', help='Purchase Requisition Currency'),
    }

    _defaults = {
        'currency_id': lambda s, c, u, ctx:
            s.pool.get('res.users').browse(
                c, u, u, context=ctx).company_id.currency_id.id,
    }

    def make_purchase_order(self, cr, uid, ids, partner_id, context=None):
        """overwrithe method to check if the pricelist select by the created
        purchase order have the same currency of the purchase requisition
        currency. If not, it look for one pricelist that fits and change it.
        If it do not find any pricelist that fit then it would raise an
        exception.
        @return True or raise and exception.
        """
        context = context or {}
        po_obj = self.pool.get('purchase.order')
        pl_obj = self.pool.get('product.pricelist')
        res = super(PurchaseRequisition, self).make_purchase_order(
            cr, uid, ids, partner_id, context=context)
        for pr_brw in self.browse(cr, uid, res.keys(), context=context):
            # extract the po_ids generated for the purchase requisition.
            # One purchase order or multiple purchase orders can be created so
            # we need to clean up this mange a list of the po_ids (not sublist
            # of ids).
            tmp_po_ids = list()
            po_ids = res.values()
            for po_id in po_ids:
                if not isinstance(po_id, (int, long)):
                    po_ids.remove(po_id)
                    tmp_po_ids.extend(po_id)
            po_ids.extend(tmp_po_ids)
            currency = dict(pr=pr_brw.currency_id)
            # check the pricelist currency
            for po_brw in po_obj.browse(cr, uid, po_ids, context=context):
                currency.update(pl=po_brw.pricelist_id.currency_id)
                if currency['pl'] != currency['pr']:
                    domain = [('currency_id', '=', currency['pr'].id)]
                    pl_ids = pl_obj.search(cr, uid, domain, context=context)
                    if pl_ids:
                        po_obj.write(cr, uid, po_brw.id, {'pricelist_id':
                                                          pl_ids[0]})
                    else:
                        currency.update(
                            pl=currency['pl'].name, pr=currency['pr'].name)
                        raise osv.except_osv(
                            _('Invalid Procedure!'),
                            _('This operation can be done because there\'s not'
                              ' exist a pricelist with the same purchase'
                              ' requisition currency. (%(pl)s != %(pr)s' %
                              currency))
        return res
