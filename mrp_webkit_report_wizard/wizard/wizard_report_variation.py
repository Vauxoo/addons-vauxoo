# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: fernandoL (fernando_ld@vauxoo.com)
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

import time

from openerp.osv import osv, fields
from openerp.tools.translate import _


class wizard_report_variation(osv.TransientModel):
    _name = 'wizard.report.variation'

    _columns = {
        'product_ids': fields.many2many('product.product', 'temp_product_rel',
            'temp_id', 'product_id', 'Productos', required=True),
        'date_start': fields.datetime('Start Date', required=True),
        'date_finished': fields.datetime('End Date', required=True),
        'type': fields.selection([('single', 'Detail'), ('group', 'Resume')],
            'Type', required=True,
            help="Only calculates for productions not in draft or cancelled"),
    }

    _defaults = {
        'date_finished': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'date_start': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
    }

    def default_get(self, cr, uid, fields, context=None):
        """ To get default values for the object.
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param fields: List of fields for which we want default values
         @param context: A standard dictionary
         @return: A dictionary which of fields with values.
        """
        if context is None:
            context = {}
        production_obj = self.pool.get('mrp.production')
        res = super(wizard_report_variation, self).default_get(
            cr, uid, fields, context=context)
        production_ids = context.get('active_ids', [])
        if not production_ids:
            return res
        prod_list = []
        for production in production_obj.browse(cr, uid, production_ids):
            prod_list.append(production.product_id.id)
        res['product_ids'] = prod_list
        return res

    def check_report(self, cr, uid, ids, context=None):
        datas = {}
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        if data.get('type') == 'single':
            myids = self.pool.get('mrp.production').search(cr, uid,
                [('product_id', 'in', data.get('product_ids')),
                ('date_finished', '>', data.get('date_start')),
                ('date_finished', '<', data.get('date_finished')),
                ('state', '<>', 'cancel')])
            if not myids:
                raise osv.except_osv(_('Advice'), _(
                    'There is no production orders for the products you\
                    selected in the range of dates you specified.'))

            datas = {
                'ids': myids,
                'model': 'wizard.report.variation',
                'form': data,
                'uid': uid,
            }

            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'webkitmrp.production_variation',
                'datas': datas,
            }

        if data.get('type') == 'group':
            data_tuple = self.generate_datas_dict(
                cr, uid, ids, context=None, child_dict=None)
            datas = data_tuple[0]
            # obtain ids of the products of children productions.
            mrp_obj = self.pool.get('mrp.production')
            mrp_data = mrp_obj.browse(cr, uid, data_tuple[1], context=context)
            child_prod_ids = {}
            datas2 = {}
            for mrp in mrp_data:
                if mrp.subproduction_ids:
                    for subp in mrp.subproduction_ids:
                        child_prod_ids.setdefault(
                            subp.product_id.id, subp.product_id.id)
                    datas2 = self.generate_datas_dict(
                        cr, uid, ids, context, child_prod_ids.values())
            datas.setdefault('child_finished', datas2 and datas2[
                             0].get('finished_dict') or [])
            datas.setdefault('child_consumed', datas2 and datas2[
                             0].get('query_dict') or [])

            ids = data_tuple[
                1]  # for some reason, we need to overwrite the ids from the wizard with the productions ones
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'webkitmrp.production_variation_group',
                'datas': datas,
            }

    def generate_datas_dict(self, cr, uid, ids, context=None, child_dict=None):
        if context is None:
            context = {}
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        company_id = context.get('company_id', user.company_id.id)
        data = self.read(cr, uid, ids)[0]
        if child_dict is None:
            prod_ids = data.get('product_ids')
        else:
            prod_ids = child_dict
        mrp_obj = self.pool.get('mrp.production')
        production_ids = mrp_obj.search(
            cr, uid, [('state', 'not in', ('draft', 'cancel')),
                    ('product_id', 'in', prod_ids),
                    ('date_finished', '>', data.get('date_start')),
                    ('date_finished', '<', data.get('date_finished')),
                    ('company_id', '=', company_id)])
        if not production_ids:
            raise osv.except_osv(_('Advice'), _(
                'There is no production orders for the products you selected\
                in the range of dates you specified.'))

        # obtain data for variation in consumed products
        cr.execute("""
            SELECT product_id, sum(quantity), sum(standard_price * quantity)
            FROM mrp_variation
            INNER JOIN product_product
                ON product_product.id = mrp_variation.product_id
            INNER JOIN product_template
                ON product_template.id = product_product.product_tmpl_id
            WHERE production_id IN
            %s
            GROUP BY product_id
        """, (tuple(production_ids),))
        records = cr.fetchall()
        consumed_variation = []
        for line in records:
            product_data = self.pool.get('product.product').browse(
                cr, uid, line[0], context=context)
            consumed_variation.append((product_data.name, line[
                                      1], product_data.uom_id.name, line[2]))

        # obtain data for variation in finished products
        cr.execute("""
            SELECT product_id, sum(quantity), sum(standard_price * quantity)
            FROM mrp_variation_finished_product
            INNER JOIN product_product
                ON product_product.id = mrp_variation_finished_product.product_id
            INNER JOIN product_template
                ON product_template.id = product_product.product_tmpl_id
            WHERE production_id IN
            %s
            GROUP BY product_id
        """, (tuple(production_ids),))
        records2 = cr.fetchall()
        finished_variation = []
        if records2:
            for line in records2:
                finished_data = self.pool.get('product.product').browse(
                    cr, uid, line[0], context=context)
                finished_variation.append((finished_data.name, line[1],
                                        finished_data.uom_id.name, line[2]))

        report_datas = {
            'ids': production_ids,
            'model': 'wizard.report.variation',
            'form': data,
            'uid': uid,
            'query_dict': consumed_variation,
            'finished_dict': finished_variation
        }
        return (report_datas, production_ids)
