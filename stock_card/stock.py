# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import osv, fields


class stock_move(osv.Model):
    _inherit = 'stock.move'
    _columns = {
        'sml_out_id': fields.many2one('stock.move', 'Out sml', select=True),
        'in_sml_ids': fields.one2many('stock.move', 'sml_out_id', 'Input sml'),

    }

    def move_line_get(self, cr, uid, ids, *args):
        res = ()
        aml_obj = self.pool.get('account.move.line')
        for l in self.browse(cr, uid, ids):
            if l.picking_id.type == 'internal':
                if getattr(l.location_id, 'account_id', False) and\
                        l.location_id.account_id.id:
                    acc_cost = l.location_id.account_id.id
                    acc_inv = l.product_id.product_tmpl_id.\
                        property_stock_account_output.id
                else:
                    acc_cost = getattr(
                        l.location_dest_id, 'account_id', False) and\
                        l.location_dest_id.account_id.id
                    acc_inv = l.product_id.product_tmpl_id.\
                        property_stock_account_input.id

                aml_cos_ids = aml_obj.find(cr, uid,
                                           ref="'%s'" % l.picking_id.name,
                                           prd_id=l.product_id.id,
                                           acc_id=acc_cost)
                aml_inv_ids = aml_obj.find(cr, uid,
                                           ref="'%s'" % l.picking_id.name,
                                           prd_id=l.product_id.id,
                                           acc_id=acc_inv)
                if aml_cos_ids and aml_inv_ids:
                    res = (aml_cos_ids[0], aml_inv_ids[0])
        return res





# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
