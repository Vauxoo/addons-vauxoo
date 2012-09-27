# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
from report import report_sxw
from osv import osv
import pooler
from tools.amount_to_text import amount_to_text
from tools.translate import _

class process_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(process_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
        'time': time,
        'get_production':self._get_production,
        'get_production_group':self._get_production_group,
        'get_print':self._get_print,
        'get_table':self._get_table,
        'get_group':self._get_group,
        'get_sin':self._get_sin,
        })
        
    def _get_production_group(self, data):
        if data['print']=='sin':
            return {}
        res=[]
        new_ids=[]
        pool = pooler.get_pool(self.cr.dbname)
        obj_prod=pool.get('mrp.production')
        for prod in obj_prod.browse(self.cr, self.uid, self.ids):
            for line in prod.move_lines:
                if line.product_id.id in data['product_ids']:
                    if line.product_id.id not in new_ids:
                        res.append({'product_id':line.product_id.id,'name':line.product_id.name,'code':line.product_id.default_code,'product_uom':line.product_id.uom_id.name,'product_qty':pool.get('product.uom')._compute_qty(self.cr, self.uid, line.product_uom.id, line.product_qty, to_uom_id=line.product_id.uom_id.id),'product_categ':line.product_id.categ_id.name})
                        new_ids.append(line.product_id.id)
                    else:
                        for r in res:
                            if r['product_id']==line.product_id.id:
                                qty=pool.get('product.uom')._compute_qty(self.cr, self.uid, line.product_uom.id, line.product_qty, to_uom_id=line.product_id.uom_id.id)
                                r['product_qty']+=qty
                    if not res:
                        res.append({'product_id':line.product_id.id,'name':line.product_id.name,'code':line.product_id.default_code,'product_uom':line.product_id.uom_id.name,'product_qty':pool.get('product.uom')._compute_qty(self.cr, self.uid, line.product_uom.id, line.product_qty, to_uom_id=line.product_id.uom_id.id),'product_categ':line.product_id.categ_id.name})
                        new_ids.append(line.product_id.id)
        """
        result={}
        for r in res:
            result.setdefault(r['product_id'],0)
            result[r['product_id']]+= r['product_qty']
        """
        return res
        
    def _get_production(self, data,prod_id):
        if data['print'] =='agrupado':
            return []
        res=[]
        pool = pooler.get_pool(self.cr.dbname)
        obj_prod=pool.get('mrp.production')
        for prod in obj_prod.browse(self.cr, self.uid, [prod_id]):
            for line in prod.move_lines:
                if line.product_id.id in data['product_ids']:
                    res.append(line)
        return res

    def _get_print(self, data):
        if data['print']=='agrupado':
            return False
        if data['print'] in ('ambos','sin'):
            return True
    
    def _get_group(self, data):
        if data['print'] in ('agrupado','ambos'):
            return ['uno']
        else:
            return []
    
    def _get_sin(self, data):
        if data['print'] in ('sin','ambos'):
            return [{'name':'Nombre','qty':'Cantidad','uom':'UOM','categ':'Categoria','real':'Real'}]
        else:
            return []
            
    def _get_table(self,data,obj):
        if data['print']=='agrupado':
            return []
        for o in obj:
            pasa=0
            if o.move_lines:
                for l in o.move_lines:
                    if l.product_id.id in data['product_ids']:
                        pasa=1
            else:
                obj.remove(o)
            if not pasa:
                obj.remove(o)
        return obj
        
report_sxw.report_sxw('report.process.report','mrp.production','addons/report_process_production/report/process_production_report.rml',parser=process_report,header=False)


