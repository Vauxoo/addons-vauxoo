# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 CachicamoERP C.A. All Rights Reserved.
#                    Javier Duran <javieredm@gmail.com>
#                    Humberto Arocha <humbertoarocha@gmail.com>
#
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
#
##############################################################################

from openerp.osv import osv, fields
from openerp.tools.sql import drop_view_if_exists

import time
import datetime
from mx.DateTime import *
from openerp.addons.decimal_precision import decimal_precision as dp


class stock_card(osv.Model):
    _name = "stock.card"
    _description = "Move by Picking Line"
    _columns = {
        'name': fields.char('Name', size=64, select=True),
        'sc_line': fields.one2many('stock.card.line',
                                   'stock_card_id',
                                   'Stock Lines', readonly=True),
        'sc_prod': fields.one2many('stock.card.product',
                                   'stock_card_id',
                                   'Stock Products', readonly=True),
        'sc_acc': fields.one2many('stock.card.account',
                                  'stock_card_id',
                                  'Accounts', readonly=True),
    }

    def find_return(self, cr, uid, ids, *args):
        cr.execute("SELECT scl.id FROM stock_card_line scl "
                   "INNER JOIN stock_picking sp on sp.id=scl.picking_id "
                   "WHERE sp.name ILIKE '%return%' ORDER BY scl.name")

        res = [x[0] for x in cr.fetchall()]
        return res

    def find_parent(self, cr, uid, ids):
        sc_line_obj = self.pool.get('stock.card.line')
        sp_obj = self.pool.get('stock.picking')
        scl_ids = self.find_return(cr, uid, ids)
        #~ print 'devoluciones: ',scl_ids
        for scl in sc_line_obj.browse(cr, uid, scl_ids):
            nb = scl.picking_id.name[
                :scl.picking_id.name.lower().find('return')-1].strip()
            #~ print 'a buscar: ',nb
            sp_ids = sp_obj.search(cr, uid, [('name', '=', nb)])
            #~ print 'posible picking padre: ',sp_ids
            if sp_ids:
                scl_ids = sc_line_obj.search(cr, uid,
                                             [('picking_id', '=', sp_ids[0]),
                                              ('product_id', '=',
                                               scl.product_id.id)])
                #~ print 'linea padre: ',scl_ids
                if scl_ids:
                    sc_line_obj.write(cr, uid, [
                                      scl.id], {'parent_id': scl_ids[0]})

        return True

    def compute_new_cost(self, cr, uid, ids):
        sc_line_obj = self.pool.get('stock.card.line')
        for sc in self.browse(cr, uid, ids):
            for scl in sc.sc_line:
                if scl.invoice_id.type not in ['in_invoice', 'in_refund']:
                    cost = scl.subtotal
                    sc_line_obj.write(cr, uid, [
                                      scl.id], {'aml_cost_cor': cost})

        return True

    def action_confirm(self, cr, uid, ids, context={}):
        drop_view_if_exists(cr, 'report_profit_picking')
        cr.execute("DELETE FROM stock_card_line")
        cr.execute("""
            create or replace view report_profit_picking as (
            select
                sm.id as id,
                to_char(sm.date_planned, 'YYYY-MM-DD:HH24:MI:SS') as name,
                sm.picking_id as picking_id,
                sp.type as type,
                sm.purchase_line_id as purchase_line_id,
                sm.sale_line_id as sale_line_id,
                sm.product_id as product_id,
                sm.location_id as location_id,
                sm.location_dest_id as location_dest_id,
                sm.id as stk_mov_id,
                sm.product_qty as picking_qty,
                sm.state as state
            from stock_picking sp
                right join stock_move sm on (sp.id=sm.picking_id)
                left join product_template pt on (pt.id=sm.product_id)
            where sm.state='done' and pt.type!='service'
            order by name
            )
        """)
        rpp_obj = self.pool.get('report.profit.picking')
        sc_line_obj = self.pool.get('stock.card.line')
        rpp_ids = rpp_obj.search(cr, uid, [])
        for rpp in rpp_obj.browse(cr, uid, rpp_ids):
            vals = {}
            vals = {
                'stock_card_id': ids[0],
                'name': rpp.name or False,
                'picking_id': rpp.picking_id and rpp.picking_id.id or False,
                'purchase_line_id': rpp.purchase_line_id and
                rpp.purchase_line_id.id or False,
                'sale_line_id': rpp.sale_line_id and
                rpp.sale_line_id.id or False,
                'product_id': rpp.product_id and
                rpp.product_id.id or False,
                'location_id': rpp.location_id and
                rpp.location_id.id or False,
                'location_dest_id': rpp.location_dest_id and
                rpp.location_dest_id.id or False,
                'stk_mov_id': rpp.stk_mov_id and rpp.stk_mov_id.id or False,
                'picking_qty': rpp.picking_qty or 0.0,
                'type': rpp.type or False,
                'state': rpp.state or False,
                'aml_cost_id': rpp.aml_cost_id and rpp.aml_cost_id.id or False,
                'invoice_line_id': rpp.invoice_line_id and
                rpp.invoice_line_id.id or False,
                'invoice_qty': rpp.invoice_qty or 0.0,
                'aml_cost_qty': rpp.aml_cost_qty or 0.0,
                'invoice_price_unit': rpp.invoice_price_unit or 0.0,
                'aml_cost_price_unit': rpp.aml_cost_price_unit or 0.0,
                'invoice_id': rpp.invoice_id and rpp.invoice_id.id or False,
                'stock_before': rpp.stock_before or 0.0,
                'stock_after': rpp.stock_after or False,
                'date_inv': rpp.date_inv or False,
                'stock_invoice': rpp.stock_invoice or 0.0,
                'aml_inv_id': rpp.aml_inv_id and rpp.aml_inv_id.id or False,
                'aml_inv_price_unit': rpp.aml_inv_price_unit or 0.0,
                'aml_inv_qty': rpp.aml_inv_qty or 0.0,

            }
            sc_line_obj.create(cr, uid, vals)

        self.find_parent(cr, uid, ids)
        self.action_done(cr, uid, ids, context)
        self.action_get_ready(cr, uid, ids, context)
        print 'LISTO MAN'
        return True

    def action_unico(self, cr, uid, ids, *args):
        cr.execute('SELECT DISTINCT product_id FROM report_profit_picking')
        res = [x[0] for x in cr.fetchall()]
        return res

    def action_scl_x_pd(self, cr, uid, ids, prd_id):
        cr.execute('SELECT id FROM stock_card_line '
                   'WHERE product_id=%s ORDER BY sequence', (prd_id,))

        res = [x[0] for x in cr.fetchall()]
        return res

    def action_sm_x_pd(self, cr, uid, ids, prd_id):
        cr.execute('SELECT id FROM report_profit_picking '
                   'WHERE product_id=%s ORDER BY name', (prd_id,))

        res = [x[0] for x in cr.fetchall()]
        return res

    def action_sm_produccion(self, cr, uid, ids, from_loc, to_loc):
        cr.execute('''SELECT id FROM report_profit_picking
                   WHERE location_id=%s AND
                         location_dest_id=%s ORDER BY name''' %
                  (from_loc, to_loc))

        res = [x[0] for x in cr.fetchall()]
        return res

    def act_procesamiento_unico(self, cr, uid, ids, lst_proc):
        cr.execute('SELECT DISTINCT product_id FROM report_profit_picking '
                   'WHERE id IN %s', (tuple(lst_proc),))
        res = [x[0] for x in cr.fetchall()]
        return res

    def lst_scl_new_cost(self, cr, uid, ids, *args):
        cr.execute("SELECT scl.id FROM stock_card_line scl  "
                   "LEFT JOIN account_invoice ai on ai.id=scl.invoice_id "
                   "WHERE ai.type NOT IN ('in_invoice', 'in_refund') "
                   "AND scl.aml_cost_id>0 AND scl.aml_inv_id>0 ")

        res = [x[0] for x in cr.fetchall()]
        return res

    def lst_scl_mov_int(self, cr, uid, ids, *args):
        cr.execute("SELECT scl.id FROM stock_card_line scl  "
                   "WHERE scl.type IN ('internal') "
                   "AND scl.aml_cost_id>0 AND scl.aml_inv_id>0 ")

        res = [x[0] for x in cr.fetchall()]
        return res

    def write_new_cost(self, cr, uid, ids, loc_ids,
                       inter_loc_ids, prod_loc_ids):
        sc_line_obj = self.pool.get('stock.card.line')
        types = {'out_invoice': -1, 'in_invoice':
                 1, 'out_refund': 1, 'in_refund': -1}

        for scl in sc_line_obj.browse(cr, uid, ids):
            if scl.invoice_id and scl.invoice_id.id:

                direction = types[scl.invoice_id.type]
                pay_amount = scl.aml_cost_cor
                l1 = {
                    'debit': direction * pay_amount > 0 and
                    direction * pay_amount or 0.0,
                    'credit': direction * pay_amount < 0 and
                    - direction * pay_amount or 0.0,
                }
                l2 = {
                    'debit': direction * pay_amount < 0 and
                    - direction * pay_amount or 0.0,
                    'credit': direction * pay_amount > 0 and
                    direction * pay_amount or 0.0,
                }
            else:
                direction = 1
                if scl.location_id.id == loc_ids and\
                        (scl.location_dest_id.id == inter_loc_ids
                         or scl.location_dest_id.id == prod_loc_ids):
                    direction = -1

                pay_amount = scl.aml_cost_cor
                l1 = {
                    'debit': direction * pay_amount > 0 and
                    direction * pay_amount or 0.0,
                    'credit': direction * pay_amount < 0 and
                    - direction * pay_amount or 0.0,
                }
                l2 = {
                    'debit': direction * pay_amount < 0 and
                    - direction * pay_amount or 0.0,
                    'credit': direction * pay_amount > 0 and
                    direction * pay_amount or 0.0,
                }

            cr.execute('UPDATE account_move_line SET debit=%s, credit=%s '
                       'WHERE id=%s' %
                      (l2['debit'], l2['credit'], scl.aml_cost_id.id))
            cr.execute('UPDATE account_move_line SET debit=%s, credit=%s '
                       'WHERE id=%s' %
                      (l1['debit'], l1['credit'], scl.aml_inv_id.id))

        return True

    def compute_compra(self, cr, uid, ids, scl_obj, q_mov, tot, prom, q_des):
        subtot = 0.0
        q_des += q_mov
        subtot = scl_obj.invoice_line_id.price_subtotal
        tot += subtot
        if q_des > 0:
            prom = tot/q_des
        else:
            prom = 0

        res = (q_des, subtot, tot, prom)
        return res

    def compute_nc_vta(self, cr, uid, ids, scl_obj, q_mov, tot, prom, q_des):
        subtot = 0.0
        if scl_obj.parent_id and scl_obj.parent_id.avg:
            prom_pad = scl_obj.parent_id.avg
        else:
            prom_pad = prom

        q_des += q_mov
        subtot = prom_pad*q_mov
        tot += subtot
        if q_des > 0:
            prom = tot/q_des
        else:
            prom = 0

        res = (q_des, subtot, tot, prom)
        return res

    def validate_nc_vta(self, cr, uid, ids, scl_obj, q_mov, tot, prom,
                        q_des, no_cp, lst_org, act_sml_id, s_ord):
        if scl_obj.parent_id:
            if scl_obj.parent_id.id in lst_org or\
                    scl_obj.parent_id.id in no_cp:
                no_cp.append(act_sml_id)
            else:
                q_bef = q_des
                q_des, subtot, tot, prom = self.compute_nc_vta(
                    cr, uid, ids, scl_obj, q_mov, tot, prom, q_des)
                value = {
                    'subtotal': subtot,
                    'total': tot,
                    'avg': prom,
                    'stk_bef_cor': q_bef,
                    'stk_aft_cor': q_des
                }
                s_ord = self.write_data(cr, uid, ids, scl_obj.id, value, s_ord)
        else:
            q_bef = q_des
            q_des, subtot, tot, prom = self.compute_nc_vta(
                cr, uid, ids, scl_obj, q_mov, tot, prom, q_des)
            value = {
                'subtotal': subtot,
                'total': tot,
                'avg': prom,
                'stk_bef_cor': q_bef,
                'stk_aft_cor': q_des
            }
            s_ord = self.write_data(cr, uid, ids, scl_obj.id, value, s_ord)

        res = (q_des, tot, prom, no_cp, s_ord)

        return res

    def compute_venta(self, cr, uid, ids, scl_obj, q_mov, tot, prom, q_des):
        subtot = 0.0
        q_des -= q_mov
        subtot = prom*q_mov
        tot -= subtot
        res = (q_des, subtot, tot, prom)
        return res

    def validate_venta(self, cr, uid, ids, scl_obj, q_mov, tot,
                       prom, q_des, no_cp, lst_org, act_sml_id, s_ord):
        if not no_cp and q_des >= q_mov:
            q_bef = q_des
            q_des, subtot, tot, prom = self.compute_venta(
                cr, uid, ids, scl_obj, q_mov, tot, prom, q_des)
            value = {
                'subtotal': subtot,
                'total': tot,
                'avg': prom,
                'stk_bef_cor': q_bef,
                'stk_aft_cor': q_des
            }
            s_ord = self.write_data(cr, uid, ids, scl_obj.id, value, s_ord)
        else:
            no_cp.append(act_sml_id)

        res = (q_des, tot, prom, no_cp, s_ord)

        return res

    def write_aml(self, cr, uid, ids, scl_obj, q_mov, prom, acc_src, acc_dest):
        move = scl_obj.stk_mov_id
        journal_id = move.product_id.categ_id.property_stock_journal.id
        ref = move.picking_id and move.picking_id.name or False
        amount = q_mov * prom
        startf = datetime.datetime.fromtimestamp(time.mktime(
            time.strptime(move.date_planned, "%Y-%m-%d %H:%M:%S")))
        date = "%s-%s-%s" % (startf.year, startf.month, startf.day)
        if move.picking_id:
            partner_id = move.picking_id.address_id and (
                move.picking_id.address_id.partner_id and
                move.picking_id.address_id.partner_id.id or False) or\
                False
        lines = [
            (0, 0, {
             'name': move.name,
                'quantity': move.product_qty,
                'product_id': move.product_id and move.product_id.id or False,
                'credit': amount,
                'account_id': acc_src,
                'ref': ref,
                'date': date,
                'partner_id': partner_id}),
            (0, 0, {
             'name': move.name,
                'product_id': move.product_id and move.product_id.id or False,
                'quantity': move.product_qty,
                'debit': amount,
                'account_id': acc_dest,
                'ref': ref,
                'date': date,
                'partner_id': partner_id})
        ]
        am_id = self.pool.get('account.move').create(cr, uid, {
            'journal_id': journal_id,
            'line_id': lines,
            'ref': ref,
            'period_id': self.pool.get('account.period').find(cr, uid,
                                                              dt=date)[0],
            'date': date,
        })

        return am_id

    def compute_nc_compra(self, cr, uid, ids, scl_obj,
                          q_mov, tot, prom, q_des):
        subtot = 0.0

        q_des -= q_mov
        subtot = scl_obj.invoice_line_id and\
            scl_obj.invoice_line_id.price_subtotal or 0.0
        tot -= subtot
        if q_des > 0:
            prom = tot/q_des
        else:
            prom = 0

        res = (q_des, subtot, tot, prom)
        return res

    def validate_nc_compra(self, cr, uid, ids, scl_obj, q_mov,
                           tot, prom, q_des, no_cp,
                           lst_org, act_sml_id, s_ord):

        if not no_cp and q_des >= q_mov:
            if scl_obj.parent_id:
                if scl_obj.parent_id.id in lst_org or\
                        scl_obj.parent_id.id in no_cp:
                    no_cp.append(act_sml_id)
                else:
                    q_bef = q_des
                    q_des, subtot, tot, prom = self.compute_nc_compra(
                        cr, uid, ids, scl_obj, q_mov, tot, prom, q_des)
                    value = {
                        'subtotal': subtot,
                        'total': tot,
                        'avg': prom,
                        'stk_bef_cor': q_bef,
                        'stk_aft_cor': q_des
                    }
                    s_ord = self.write_data(
                        cr, uid, ids, scl_obj.id, value, s_ord)
            else:
                q_bef = q_des
                q_des, subtot, tot, prom = self.compute_nc_compra(
                    cr, uid, ids, scl_obj, q_mov, tot, prom, q_des)
                value = {
                    'subtotal': subtot,
                    'total': tot,
                    'avg': prom,
                    'stk_bef_cor': q_bef,
                    'stk_aft_cor': q_des
                }
                s_ord = self.write_data(cr, uid, ids, scl_obj.id, value, s_ord)
        else:
            no_cp.append(act_sml_id)

        res = (q_des, tot, prom, no_cp, s_ord)
        return res

    def write_data(self, cr, uid, ids, scl_id, vals, seq):
        sc_line_obj = self.pool.get('stock.card.line')
        seq += 1
        vals.update({'sequence': seq})
        sc_line_obj.write(cr, uid, scl_id, vals)
        return seq

    def validate_procesamiento(self, cr, uid, ids, scl_obj, q_mov,
                               subtot, tot, prom, q_des, lst_org, act_sml_id):

        for scl in scl_obj.in_sml_ids:
            subtot += scl.subtotal

        q_des += q_mov
        tot += subtot
        prom = tot/q_des

        res = (q_des, subtot, tot, prom)

        return res

    def action_get_ready(self, cr, uid, ids, context={}):
        product_ids = self.action_unico(cr, uid, ids)
        aml_obj = self.pool.get('account.move.line')
        scpm_cost_obj = self.pool.get('stock.card.product.move.cost')
        scpm_inv_obj = self.pool.get('stock.card.product.move.inv')
        scal_obj = self.pool.get('stock.card.account.lines')
        for id in ids:
            scp_obj = self.pool.get('stock.card.product')
            scp_obj.unlink(cr, uid, [
                           line.id for line in self.browse(cr,
                                                           uid, id).sc_prod])
            sca_obj = self.pool.get('stock.card.account')
            sca_obj.unlink(cr, uid, [
                           line.id for line in self.browse(cr,
                                                           uid, id).sc_acc])
            dict_inv = {}
            dict_cst = {}

            dict_prod = {}
            dict_inv_prod = {}
            dict_cst_prod = {}

            for prod_id in product_ids:
                dict_prod[prod_id] = scp_obj.create(cr, uid, {
                    'stock_card_id': id,
                    'product_id': prod_id,
                    'scl_ids': [(6, 0, self.action_scl_x_pd(cr, uid,
                                                            ids, prod_id))]
                })
                prod_brw = self.pool.get('product.product').browse(
                    cr, uid, prod_id, context)

                ##################################################
                # ACUMULANDO LOS ASIENTOS CONTABLES POR CUENTAS  #
                ##################################################

                if not dict_inv.get(prod_brw.product_tmpl_id.
                                    property_stock_account_input.id, False):
                    dict_inv[prod_brw.product_tmpl_id.
                             property_stock_account_input.id] =\
                        aml_obj.search(cr, uid,
                            [('account_id', '=',
                              prod_brw.product_tmpl_id.
                              property_stock_account_input.
                              id)])

                if not dict_cst.get(prod_brw.product_tmpl_id.
                                    property_account_expense.id, False):
                    dict_cst[prod_brw.product_tmpl_id.
                             property_account_expense.id] = \
                        aml_obj.search(cr, uid,
                            [('account_id', '=', prod_brw.product_tmpl_id.
                              property_account_expense.id)])

                ##########################################
                # no todos los asientos se estan cargando#
                ##########################################

                dict_inv_prod[prod_id] = []
                dict_cst_prod[prod_id] = []

            # Eliminando aquellos asientos contables que ya estan asignados en
            # una scl

            for scl in self.browse(cr, uid, id).sc_line:
                if scl.aml_inv_id and\
                        dict_inv.get(scl.aml_inv_id.account_id.id, False):
                    if scl.aml_inv_id.id in\
                            dict_inv[scl.aml_inv_id.account_id.id]:
                        dict_inv[scl.aml_inv_id.account_id.id].remove(
                            scl.aml_inv_id.id)

                if scl.aml_cost_id and\
                        dict_cst.get(scl.aml_cost_id.account_id.id, False):
                    if scl.aml_cost_id.id in\
                            dict_cst[scl.aml_cost_id.account_id.id]:
                        dict_cst[scl.aml_cost_id.account_id.id].remove(
                            scl.aml_cost_id.id)

            #~ print 'OTROS 5 SEG. MAS'
            #~ time.sleep(5)
            for key in dict_inv:
                for elem in dict_inv[key]:
                    aml_brw = aml_obj.browse(cr, uid, elem, context)
                    if aml_brw.product_id and\
                            aml_brw.product_id.id in product_ids:
                        dict_inv_prod[aml_brw.product_id.id].append(elem)
                        dict_inv[key].remove(elem)

            for key in dict_cst:
                for elem in dict_cst[key]:
                    aml_brw = aml_obj.browse(cr, uid, elem, context)
                    if aml_brw.product_id and aml_brw.product_id.id in\
                            product_ids:
                        dict_cst_prod[aml_brw.product_id.id].append(elem)
                        dict_cst[key].remove(elem)

            for key in dict_prod:
                dict_inv_prod[key].sort()
                for i in dict_inv_prod[key]:
                    scpm_inv_obj.create(cr, uid, {
                                        'scp_id': dict_prod[key],
                                        'aml_id': i})

                dict_cst_prod[key].sort()
                for i in dict_cst_prod[key]:
                    scpm_cost_obj.create(cr, uid, {
                                         'scp_id': dict_prod[key],
                                         'aml_id': i})

            #~ # Crear los asientos que queden

            for key in dict_inv:
                if dict_inv.get(key, False):
                    sca_id = sca_obj.create(cr, uid, {
                                            'stock_card_id': id,
                                            'account_id': key,
                                            })
                    for elem in dict_inv[key]:
                        scal_obj.create(cr, uid, {
                            'sca_id': sca_id,
                            'aml_id': elem,
                        })

            for key in dict_cst:
                if dict_cst.get(key, False):
                    sca_id = sca_obj.create(cr, uid, {
                                            'stock_card_id': id,
                                            'account_id': key,
                                            })
                    for elem in dict_cst[key]:
                        scal_obj.create(cr, uid, {
                            'sca_id': sca_id,
                            'aml_id': elem,
                        })

    def action_done(self, cr, uid, ids, context={}):
        loc_obj = self.pool.get('stock.location')
        product_ids = self.action_unico(
            cr, uid, ids)  # productos unicos de todos los items de la vista
        # loc_ids = 11
        loc_ids = loc_obj.search(cr, uid, [('name', '=', 'Stock')])[0]
        inter_loc_ids = loc_obj.search(cr, uid, [
                                       ('name', '=', 'Uso_Interno')])[0]
        prod_loc_ids = loc_obj.search(cr, uid, [
                                      ('name', '=', 'Procesamiento')])[0]

        Dict = {}
        for prod_id in product_ids:
            Dict[prod_id] = {
                'sml':          self.action_sm_x_pd(cr, uid, ids, prod_id),
                'no_cump':      [],
                'total':        0.0,
                'avg':          0.0,
                'qda':          0.0,
                'cont':         False,
                'seq':          0,
            }

        for prod_id in product_ids:
            self.procesar_producto(cr, uid, ids, prod_id, Dict, loc_ids,
                                   inter_loc_ids, prod_loc_ids)
        # compute_new_cost para movimientos internos
        self.compute_new_cost(cr, uid, ids)
        lst_scl_refac = self.lst_scl_new_cost(cr, uid, ids)
        # lista a refactorizar de mov internos(asiento inv y costo y de tipo
        # interno)
        lst_scl_refac_mov_int = self.lst_scl_mov_int(cr, uid, ids)
        # unir las dos lista a refactorizar
        self.write_new_cost(cr, uid, lst_scl_refac+lst_scl_refac_mov_int,
                            loc_ids, inter_loc_ids, prod_loc_ids)
        return True

    def procesar_producto(self, cr, uid, ids, prod_id, Dict,
                          loc_ids, inter_loc_ids, prod_loc_ids, pending=False):
        '''
        Concepto de prueba de Humberto Arocha para
        procesamiento recursivo de de stock card line
        '''
        rpp_obj = self.pool.get('report.profit.picking')
        sc_line_obj = self.pool.get('stock.card.line')
        product = Dict[prod_id]
        sml_x_pd_id = product['sml']
        no_cump = product['no_cump']
        total = product['total']
        avg = product['avg']
        qda = product['qda']
        cont = product['cont']
        seq = product['seq']
        def_code = self.pool.get('product.product').browse(
            cr, uid, prod_id).default_code.strip()

        while sml_x_pd_id:
            sml_id = sml_x_pd_id.pop(0)
            value = {}
            if not cont:
                cont = True
                q = 0.0
                subtotal = 0.0
                qda = 0.0
                cr.execute('SELECT standard_price,product_qty FROM lst_cost '
                           'WHERE default_code=%s', (def_code,))
                res = cr.fetchall()
                if res and res[0][1]:
                    #~ print 'encontre costo inicccc'
                    avg, q = res[0]
                else:
                    rpp = rpp_obj.browse(cr, uid, sml_id)
                    if rpp.location_dest_id.id == loc_ids and\
                            rpp.invoice_id.type == 'in_invoice':
                        q = rpp.picking_qty
                        avg = rpp.invoice_line_id.price_subtotal / q
                    else:
                        no_cump.append(sml_id)
                        continue
                total = avg*q
                subtotal = avg*q
                qda = q
                seq += 1
                value = {
                    'subtotal': subtotal,
                    'total': total,
                    'avg': avg,
                    'stk_bef_cor': 0.0,
                    'stk_aft_cor': qda,
                    'sequence': seq
                }
                scl_id = sc_line_obj.search(cr, uid, [
                                            ('stk_mov_id', '=', sml_id)])
                sc_line_obj.write(cr, uid, scl_id, value)
            else:
                rpp = rpp_obj.browse(cr, uid, sml_id)
                q = rpp.picking_qty
                scl_id = sc_line_obj.search(cr, uid, [
                                            ('stk_mov_id', '=', sml_id)])
                scl = sc_line_obj.browse(cr, uid, scl_id)[0]
                if rpp.location_id.id == loc_ids and\
                        rpp.invoice_id.type == 'out_invoice':
                    qda, total, avg, no_cump, seq = \
                        self.validate_venta(cr, uid, ids, scl, q, total, avg,
                                            qda, no_cump, sml_x_pd_id, sml_id,
                                            seq)
                if rpp.location_id.id == loc_ids and\
                        (rpp.invoice_id.type == 'in_refund' or
                         rpp.invoice_id.type == 'in_invoice'):
                    qda, total, avg, no_cump, seq = \
                        self.validate_nc_compra(cr, uid, ids, scl, q, total,
                                                avg, qda, no_cump,
                                                sml_x_pd_id, sml_id, seq)
                if rpp.location_dest_id.id == loc_ids and\
                        rpp.invoice_id.type == 'in_invoice':
                    q_bef = qda
                    qda, subtotal, total, avg = self.compute_compra(
                        cr, uid, ids, scl, q, total, avg, qda)
                    value = {
                        'subtotal': subtotal,
                        'total': total,
                        'avg': avg,
                        'stk_bef_cor': q_bef,
                        'stk_aft_cor': qda
                    }
                    seq = self.write_data(cr, uid, ids, scl.id, value, seq)
                    if no_cump:
                        no_cump.extend(sml_x_pd_id)
                        no_cump = []
                if rpp.location_dest_id.id == loc_ids and\
                        rpp.invoice_id.type == 'out_refund':
                    qda, total, avg, no_cump, seq = \
                        self.validate_nc_vta(cr, uid, ids, scl, q, total,
                                             avg, qda, no_cump, sml_x_pd_id,
                                             sml_id, seq)

                    if no_cump and not scl.parent_id:
                        no_cump.extend(sml_x_pd_id)
                        sml_x_pd_id = no_cump
                        no_cump = []

                # DESTINO USO INTERNO
                if rpp.location_id.id == loc_ids and\
                        rpp.location_dest_id.id == inter_loc_ids:
                    qda, total, avg, no_cump, seq = \
                        self.validate_venta(cr, uid, ids, scl, q, total, avg,
                                            qda, no_cump, sml_x_pd_id,
                                            sml_id, seq)
                    valores = {}
                    if not (rpp.aml_cost_id or rpp.aml_inv_id):
                        move = scl.stk_mov_id
                        acc_src = move.product_id.product_tmpl_id.\
                            property_stock_account_output.id
                        if move.location_dest_id.account_id:
                            acc_dest = move.location_dest_id.account_id.id

                        acc_mov_id = self.write_aml(
                            cr, uid, ids, scl, q, avg, acc_src, acc_dest)
                        acc_mov_obj = self.pool.get(
                            'account.move').browse(cr, uid, acc_mov_id)
                        for aml in acc_mov_obj.line_id:
                            valores.update({
                                'aml_cost_qty': aml.quantity or 0.0,
                                'aml_cost_price_unit': avg,
                                'aml_inv_qty': aml.quantity or 0.0,
                                'aml_inv_price_unit': avg})
                            if aml.debit:
                                valores.update({'aml_cost_id': aml.id})
                            if aml.credit:
                                valores.update({'aml_inv_id': aml.id})

                        sc_line_obj.write(cr, uid, scl.id, valores)

                # DESTINO PROCESAMIENTO
                if rpp.location_id.id == loc_ids and\
                        rpp.location_dest_id.id == prod_loc_ids:
                    qda, total, avg, no_cump, seq = \
                        self.validate_venta(cr, uid, ids, scl, q, total,
                                            avg, qda, no_cump, sml_x_pd_id,
                                            sml_id, seq)
                    valores = {}
                    if not (rpp.aml_cost_id or rpp.aml_inv_id):
                        move = scl.stk_mov_id
                        acc_src = move.product_id.product_tmpl_id.\
                            property_stock_account_output.id
                        if move.location_dest_id.account_id:
                            acc_dest = move.location_dest_id.account_id.id

                        acc_mov_id = self.write_aml(
                            cr, uid, ids, scl, q, avg, acc_src, acc_dest)
                        acc_mov_obj = self.pool.get(
                            'account.move').browse(cr, uid, acc_mov_id)
                        for aml in acc_mov_obj.line_id:
                            valores.update({
                                'aml_cost_qty': aml.quantity or 0.0,
                                'aml_cost_price_unit': avg,
                                'aml_inv_qty': aml.quantity or 0.0,
                                'aml_inv_price_unit': avg})
                            if aml.debit:
                                valores.update({'aml_cost_id': aml.id})
                            if aml.credit:
                                valores.update({'aml_inv_id': aml.id})

                        sc_line_obj.write(cr, uid, scl.id, valores)
                # DESDE PROCESAMIENTO  PARA STOCK
                if rpp.location_id.id == prod_loc_ids and\
                        rpp.location_dest_id.id == loc_ids:
                    q_bef = qda
                    qda += q
                    subtotal = 0.0
                    for i in scl.in_sml_ids:
                        i_id = rpp_obj.search(cr, uid, [(
                            'stk_mov_id', '=', i.stk_mov_id.id)])[0]

                        if i_id in Dict[i.product_id.id]['sml']:
                            self.procesar_producto(cr, uid, ids,
                                                   i.product_id.id, Dict,
                                                   loc_ids, inter_loc_ids,
                                                   prod_loc_ids, i_id)
                            subtotal += sc_line_obj.browse(cr, uid,
                                                           i.id).subtotal
                        else:
                            subtotal += sc_line_obj.browse(
                                cr, uid, i.id).subtotal
                    total += subtotal
                    avg = qda and total/qda or 0.0
                    value = {
                        'subtotal': subtotal,
                        'total': total,
                        'avg': qda and total/qda or 0.0,
                        'stk_bef_cor': q_bef,
                        'stk_aft_cor': qda,
                        'aml_cost_price_unit': subtotal/q
                    }
                    seq = self.write_data(cr, uid, ids, scl.id, value, seq)

                    if no_cump:
                        no_cump.extend(sml_x_pd_id)
                        sml_x_pd_id = no_cump
                        no_cump = []

                    valores = {}
                    if not (rpp.aml_cost_id or rpp.aml_inv_id):
                        move = scl.stk_mov_id
                        if move.location_id.account_id:
                            acc_src = move.location_id.account_id.id

                        acc_dest = move.product_id.product_tmpl_id.\
                            property_stock_account_input.id

                        acc_mov_id = self.write_aml(cr, uid, ids, scl, q,
                                                    q and subtotal/q or 0,
                                                    acc_src, acc_dest)
                        acc_mov_obj = self.pool.get(
                            'account.move').browse(cr, uid, acc_mov_id)
                        for aml in acc_mov_obj.line_id:
                            valores.update({
                                'aml_cost_qty': aml.quantity or 0.0,
                                'aml_cost_price_unit': avg,
                                'aml_inv_qty': aml.quantity or 0.0,
                                'aml_inv_price_unit': avg})
                            if aml.credit:
                                valores.update({'aml_cost_id': aml.id})
                            if aml.debit:
                                valores.update({'aml_inv_id': aml.id})

                        sc_line_obj.write(cr, uid, scl.id, valores)

                # NO HAY MAS COMPRAS O NC VENTAS Y QUEDAN MOVIMIENTOS
                if no_cump and not sml_x_pd_id:
                    while no_cump:
                        sml_id = no_cump.pop(0)

            if sml_id == pending and pending not in no_cump:
                # Actualizar el Dict con los valores que quedan remanentes
                break
        Dict[prod_id].update({'sml': sml_x_pd_id,
                              'no_cump': no_cump,
                             'total': total,
                             'avg': avg,
                             'qda': qda,
                             'cont': cont})
        return True


class stock_card_line(osv.Model):
    _name = "stock.card.line"
    _description = "Move by Picking Line"
    _order = 'sequence'

    def _get_scl_out(self, cr, uid, ids, field_name, arg, context={}):
        result = {}
        for scl in self.browse(cr, uid, ids, context):
            result[scl.id] = False
            if scl.stk_mov_id.sml_out_id:
                scl_out_ids = self.search(cr, uid, [(
                    'stk_mov_id.id', '=', scl.stk_mov_id.sml_out_id.id)])
                if scl_out_ids:
                    scl_obj = self.browse(cr, uid, scl_out_ids[0])
                    result[scl.id] = (scl_obj.id, scl_obj.name)
        return result

    def _get_scl_from_sm(self, cr, uid, ids, context={}):
        scl_ids = []
        scl_ids = self.pool.get('stock.card.line').search(
            cr, uid, [('stk_mov_id', 'in', ids)], context=context)
        return scl_ids

    def _get_scl_from_scl(self, cr, uid, ids, context={}):
        scl_ids = []
        for scl in self.browse(cr, uid, ids, context):
            if scl.stk_mov_id.in_sml_ids:
                scl_ids = self._get_scl_from_sm(cr, uid, [
                                                x.id for x in
                                                scl.stk_mov_id.in_sml_ids],
                                                context)
        return scl_ids

    _columns = {
        'stock_card_id': fields.many2one('stock.card', 'Stock card',
                                         readonly=True, select=True),
        'name': fields.char('Date', size=20, readonly=True, select=True),
        'picking_id': fields.many2one('stock.picking', 'Picking',
                                      readonly=True, select=True),
        'purchase_line_id': fields.many2one('purchase.order.line',
                                            'Purchase Line',
                                            readonly=True, select=True),
        'sale_line_id': fields.many2one('sale.order.line',
                                        'Sale Line', readonly=True,
                                        select=True),
        'product_id': fields.many2one('product.product', 'Product',
                                      readonly=True, select=True),
        'location_id': fields.many2one('stock.location', 'Source Location',
                                       readonly=True, select=True),
        'location_dest_id': fields.many2one('stock.location', 'Dest. Location',
                                            readonly=True, select=True),
        'stk_mov_id': fields.many2one('stock.move', 'Picking line',
                                      readonly=True, select=True),
        'picking_qty': fields.float('Picking quantity',
                                    digits_compute=dp.get_precision('Account'),
                                    readonly=True),
        'type': fields.selection([
            ('out', 'Sending Goods'),
            ('in', 'Getting Goods'),
            ('internal', 'Internal'),
            ('delivery', 'Delivery')
        ], 'Type', readonly=True, select=True),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('waiting', 'Waiting'),
            ('confirmed', 'Confirmed'),
            ('assigned', 'Available'),
            ('done', 'Done'),
            ('cancel', 'Cancelled')
        ], 'Status', readonly=True, select=True),
        'aml_cost_id': fields.many2one('account.move.line',
                                       string='Cost entry', readonly=True,
                                       select=True),
        'invoice_line_id': fields.many2one('account.invoice.line',
                                           string='Invoice line',
                                           readonly=True, select=True),
        'invoice_qty': fields.float(string='Invoice quantity',
                                    digits_compute=dp.get_precision('Account'),
                                    readonly=True),
        'aml_cost_qty': fields.float(string='Cost entry quantity',
                                     digits_compute=
                                     dp.get_precision('Account'),
                                     readonly=True),
        'invoice_price_unit': fields.float(string='Invoice price unit',
                                           digits_compute=
                                                  dp.get_precision('Account'),
                                                  readonly=True),
        'aml_cost_price_unit': fields.float(string='Cost entry price unit',
                                            digits_compute=
                                                   dp.get_precision('Account'),
                                                   readonly=True),
        'invoice_id': fields.many2one('account.invoice', string='Invoice',
                                      readonly=True, select=True),
        'stock_before': fields.float(string='Stock before',
                                     digits_compute=
                                     dp.get_precision('Account'),
                                     readonly=True),
        'stock_after': fields.float(string='Stock after',
                                    digits_compute=dp.get_precision('Account'),
                                    readonly=True),
        'date_inv': fields.char(string='Date invoice', size=20, readonly=True,
                                select=True),
        'stock_invoice': fields.float(string='Stock invoice',
                                      digits_compute=
                                      dp.get_precision('Account'),
                                      readonly=True),
        'subtotal': fields.float(string='Subtotal',
                                 digits_compute=dp.get_precision('Account'),
                                 readonly=True),
        'total': fields.float(string='Total',
                              digits_compute=dp.get_precision('Account'),
                              readonly=True),
        'avg': fields.float(string='Price Avg',
                            digits_compute=dp.get_precision('Account'),
                            readonly=True),
        'parent_id': fields.many2one('stock.card.line', 'Parent',
                                     readonly=True, select=True),
        'sequence': fields.integer('Sequence', readonly=True),
        'stk_bef_cor': fields.float(string='Stock before cal',
                                    digits_compute=dp.get_precision('Account'),
                                    readonly=True),
        'stk_aft_cor': fields.float(string='Stock after cal',
                                    digits_compute=dp.get_precision('Account'),
                                    readonly=True),
        'sml_out_id': fields.function(_get_scl_out, method=True,
                                      type='many2one',
                                      relation='stock.card.line',
                                      store={
                                      'stock.card.line': (_get_scl_from_scl,
                                                          None, 50),
                                      'stock.move': (_get_scl_from_sm,
                                                     None, 50),
                                      }, string='Out sml', select=True, ),
        'in_sml_ids': fields.one2many('stock.card.line',
                                      'sml_out_id', 'Input sml'),
        'aml_inv_id': fields.many2one('account.move.line',
                                      string='Inv entry', readonly=True,
                                      select=True),
        'aml_inv_price_unit': fields.float(string='Inv entry price unit',
                                           digits_compute=
                                           dp.get_precision('Account'),
                                           readonly=True),
        'aml_inv_qty': fields.float(string='Inv entry quantity',
                                    digits_compute=dp.get_precision('Account'),
                                    readonly=True),
        'aml_cost_cor': fields.float(string='Cost entry cal',
                                     digits_compute=
                                     dp.get_precision('Account'),
                                     readonly=True),

    }


class stock_card_product(osv.Model):
    _name = 'stock.card.product'
    _description = 'Products in Stock Card'
    _columns = {
        'stock_card_id': fields.many2one('stock.card',
                                         'Stock card',
                                         readonly=True,
                                         select=True),
        'product_id': fields.many2one('product.product',
                                      'Product', readonly=True,
                                      select=True),
        'scl_ids': fields.one2many('stock.card.line',
                                   'scp_id', 'Stock Card Lines'),
        'scpm_cost_ids': fields.one2many('stock.card.product.move.cost',
                                         'scp_id', 'Cost Moves'),
        'scpm_inv_ids': fields.one2many('stock.card.product.move.inv',
                                        'scp_id', 'Inventory Moves'),
    }
    _rec_name = 'product_id'


class stock_card_account(osv.Model):
    _name = 'stock.card.account'
    _description = 'Accounts in Stock Card'
    _columns = {
        'stock_card_id': fields.many2one('stock.card', 'Stock card',
                                         readonly=True, select=True,
                                         ondelete='cascade'),
        'account_id': fields.many2one('account.account', 'Account',
                                      readonly=True, select=True),
        'aml_ids': fields.one2many('stock.card.account.lines', 'sca_id',
                                   'Accounting Entries'),
    }
    _rec_name = 'stock_card_id'


class stock_card_account_lines(osv.Model):
    _name = 'stock.card.account.lines'
    _columns = {
        'sca_id': fields.many2one('stock.card.account',
                                  'Product Group', ondelete='cascade'),
        'aml_id': fields.many2one('account.move.line',
                                  string='Account Entry',
                                  readonly=True, select=True),
    }
    _rec_name = 'sca_id'


class stock_card_lines(osv.Model):
    _inherit = 'stock.card.line'
    _columns = {
        'scp_id': fields.many2one('stock.card.product', 'Product Group'),
    }


class stock_card_product_move_cost(osv.Model):
    _name = 'stock.card.product.move.cost'
    _columns = {
        'scp_id': fields.many2one('stock.card.product', 'Product Group',
                                  ondelete='cascade'),
        'aml_id': fields.many2one('account.move.line', string='Account Entry',
                                  readonly=True, select=True),
    }
    _rec_name = 'scp_id'


class stock_card_product_move_inv(osv.Model):
    _name = 'stock.card.product.move.inv'
    _columns = {
        'scp_id': fields.many2one('stock.card.product', 'Product Group',
                                  ondelete='cascade'),
        'aml_id': fields.many2one('account.move.line', string='Account Entry',
                                  readonly=True, select=True),
    }
    _rec_name = 'scp_id'


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
