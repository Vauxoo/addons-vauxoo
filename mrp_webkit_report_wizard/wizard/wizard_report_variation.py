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

from osv import osv, fields
from tools.translate import _


class wizard_report_variation(osv.osv_memory):
    _name = 'wizard.report.variation'

    _columns = {
        'product_ids': fields.many2many('product.product','temp_product_rel','temp_id','product_id','Productos', required=True),
        'date_start': fields.datetime('Start Date'),
        'date_finished': fields.datetime('End Date', required=True),
        'type': fields.selection([('single','Detail'),('group','Resume')], 'Type', required=True, help="Only calculates for productions not in draft or cancelled"),
    }
    
    _defaults = {
        'date_finished': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
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
        prod_obj = self.pool.get('product.product')
        production_obj = self.pool.get('mrp.production')
        res = super(wizard_report_variation, self).default_get(cr, uid, fields, context=context)
        production_ids = context.get('active_ids', [])
        if not production_ids:
            return res
        prod_list=[]
        for production in production_obj.browse(cr,uid,production_ids):
            for line in production.move_lines:
                prod_list.append(line.product_id.id)
        res['product_ids']=prod_list
        return res
        
    def check_report(self, cr, uid, ids, context=None):
        datas = {}
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        if data.get('type') == 'single':
            myids = self.pool.get('mrp.production').search(cr, uid, [('product_id', 'in', data.get('product_ids')),('date_planned', '>', data.get('date_start')),('date_planned', '<', data.get('date_finished')),('state', '<>', 'cancel')])
            if not myids:
                raise osv.except_osv(_('Advice'), _('There is no production orders for the products you selected in the range of dates you specified.'))
            
            
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
            user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
            company_id = context.get('company_id', user.company_id.id)
            prod_ids = tuple(data.get('product_ids'))
            cr.execute("""
SELECT product_id, sum(standard_price * quantity) AS mul FROM mrp_variation
INNER JOIN product_product
   ON product_product.id = mrp_variation.product_id
INNER JOIN product_template
   ON product_template.id = product_product.product_tmpl_id
WHERE production_id IN (

 SELECT id FROM mrp_production AS mp
 WHERE mp.date_planned > %s
  AND mp.date_planned < %s
  AND mp.product_id in %s
  AND state NOT IN ('cancel' ,'draft')
  AND company_id = %s
 )
GROUP BY product_id
            """, (data.get('date_start'), data.get('date_finished'), prod_ids, company_id))
            records = cr.fetchall()
            if not records:
                raise osv.except_osv(_('Advice'), _('There is no production orders for the products you selected in the range of dates you specified.'))
            
            datas = {
                'ids': [],
                'model': 'wizard.report.variation',
                'form': data,
                'uid': uid,
                'query_dict': records
            }
            
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'webkitmrp.production_variation_group',
                'datas': datas,
            }
wizard_report_variation()
