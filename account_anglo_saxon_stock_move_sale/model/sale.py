##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C)
#    2004-2010 Tiny SPRL (<http://tiny.be>).
#    2009-2010 Veritos (http://veritos.nl).
#    All Rights Reserved
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
from openerp.tools.translate import _
from openerp.osv import osv, fields


class SaleOrder(osv.osv):

    _inherit = "sale.order"
    _columns = {
        'aml_ids': fields.one2many(
            'account.move.line',
            'sale_id',
            # domain='[(account_id.reconcile, "=", True)]',
            string='Account Move Lines'),
    }

    def view_accrual(self, cr, uid, ids, context=None):
        ids = isinstance(ids, (int, long)) and [ids] or ids
        context = context or {}
        res = []
        for sale_brw in self.browse(cr, uid, ids, context=context):
            res += [aml_brw.id
                    for aml_brw in sale_brw.aml_ids
                    # This shall be taken away when fixing domain in aml_ids
                    if aml_brw.account_id.reconcile
                    ]
        return {
            'domain': "[('id','in',\
                [" + ','.join([str(item) for item in res]) + "])]",
            'name': _('Journal Items'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move.line',
            'view_id': False,
            'type': 'ir.actions.act_window'
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
