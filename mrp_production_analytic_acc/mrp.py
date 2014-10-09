# -*- coding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: Luis Torres (luis_t@vauxoo.com),Rodo (rodo@vauxoo.com)
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
from openerp.osv import osv, fields


class mrp_production(osv.Model):
    _inherit = "mrp.production"

    def product_id_change(self, cr, uid, ids, product_id, context=None):
        bom_obj = self.pool.get('mrp.bom')
        res = super(mrp_production, self).product_id_change(
            cr, uid, ids, product_id, context=context)
        if not product_id:
            res['value']['analytic_acc_rm'] = False
            res['value']['analytic_acc_fg'] = False
        if res['value']['bom_id']:
            bom = bom_obj.browse(cr, uid, [res[
                                 'value']['bom_id']], context=context)
            res['value']['analytic_acc_rm'] = bom and bom[
                0].analytic_acc_rm.id or False
            res['value']['analytic_acc_fg'] = bom and bom[
                0].analytic_acc_fg.id or False
        return res

    def bom_id_change(self, cr, uid, ids, bom_id, context=None):
        bom_obj = self.pool.get('mrp.bom')
        res = super(mrp_production, self).bom_id_change(
            cr, uid, ids, bom_id, context=context)
        if bom_id:
            bom = bom_obj.browse(cr, uid, [bom_id], context=context)
            res['value']['analytic_acc_rm'] = bom and bom[
                0].analytic_acc_rm.id or False
            res['value']['analytic_acc_fg'] = bom and bom[
                0].analytic_acc_fg.id or False
        else:
            res['value']['analytic_acc_rm'] = False
            res['value']['analytic_acc_fg'] = False
        return res

    def _make_production_internal_shipment_line(self, cr, uid, production_line,
                                                shipment_id, parent_move_id,
                                                destination_location_id=False,
                                                context=None):
        stock_move = self.pool.get('stock.move')
        production = production_line.production_id
        res = super(
            mrp_production, self)._make_production_internal_shipment_line(cr,
                        uid, production_line, shipment_id,
                        parent_move_id,
                        destination_location_id=destination_location_id,
                        context=context)
        print res
        if parent_move_id and production.analytic_acc_rm:
            stock_move.write(cr, uid, [parent_move_id], {
                             'analytic_acc': production.analytic_acc_rm.id},
                             context=context)
        if res and production.analytic_acc_rm:
            stock_move.write(cr, uid, [res], {
                             'analytic_acc': production.analytic_acc_rm.id},
                             context=context)
        return res

    def _make_production_produce_line(self, cr, uid, production, context=None):
        stock_move = self.pool.get('stock.move')
        res = super(mrp_production, self)._make_production_produce_line(
            cr, uid, production, context=context)
        if production.analytic_acc_fg:
            stock_move.write(cr, uid, [res], {
                             'analytic_acc': production.analytic_acc_fg.id},
                             context=context)
        return res

        def _make_production_consume_line(self, cr, uid, production_line,
                    parent_move_id, source_location_id=False, context=None):
            stock_move = self.pool.get('stock.move')
            production = production_line.production_id
            res = super(mrp_production, self)._make_production_consume_line(
                cr, uid, production_line, parent_move_id,
                source_location_id=False, context=context)
            if production.analytic_acc_rm.id:
                stock_move.write(cr, uid, [res], {
                    'analytic_acc': production.analytic_acc_rm.id},
                    context=context)
            return res

    _columns = {
        'analytic_acc_rm': fields.many2one('account.analytic.account',
            'Analytic Account RM', readonly=True,
            states={'draft': [('readonly', False)]}),
        'analytic_acc_fg': fields.many2one('account.analytic.account',
            'Analytic Account FG', readonly=True,
            states={'draft': [('readonly', False)]})
    }


class mrp_bom(osv.Model):
    _inherit = "mrp.bom"

    _columns = {
        'analytic_acc_rm': fields.many2one('account.analytic.account',
            'Analytic Account RM',),
        'analytic_acc_fg': fields.many2one('account.analytic.account',
            'Analytic Account FG',)
    }
