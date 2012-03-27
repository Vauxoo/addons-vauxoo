#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Vauxoo C.A.           
#    Planified by: Nhomar Hernandez
#    Audited by: Vauxoo C.A.
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
################################################################################

from osv import fields, osv
import tools
from tools.translate import _
from tools import config
import netsvc
import decimal_precision as dp


class compute_cost(osv.osv_memory):

    
    _name = 'compute.cost'
    _columns = {
        'product_ids':fields.many2many('product.product','product_rel','product1','product2','Product',help="Select the product to compute cost"),
        'product':fields.boolean('Product',help="To select compute by product"),
        'categ':fields.boolean('Category',help="To select compute by category"),
        'categ_ids':fields.many2many('product.category','categ_rel','categ1','categ2','Product Category',help="Select the category to compute cost"),
        'fiscalyear_id':fields.many2one('account.fiscalyear','Fiscal Year',help="Fiscal Year to search invoice between indicated period"),
        'period_id':fields.many2one('account.period','Period',help="Period to search invoice between indicated period"),
        'all':fields.boolean('ALL',help="To compute cost for all products"),
    }
    
    
    def list_cost(self,cicle,ids_inv):
        lista = []
        
        for d in cicle:
            aux2 = d[0]
            while aux2 != True:
                aux2 = aux2 - 1
                if aux2 in ids_inv:
                    cost = ids_inv[aux2]
                    aux2 = True
            lista.append((d[3], d[3] * cost, cost and cost or 0, d[4] ))
        return lista
    
    #~ TODO EL mismo algoritmo para LIFO,
     #~  ""  "" FIFO, 
    #~ meter el concepto de ajuste de inventario
    #~  meter concepto de produccion
    
    def compute_cost(self,cr,uid,ids,context=None,products=False,period=False):
        '''
        Method to compute coste from porduct invoice from a wizard or called from other method
        
        @param products IDS list of products to compute cost from invoices
        @param period ids of period to give range to compute cost 
        @param ids ids of wizard for method call 
        
        '''
        if context is None:
            context = {}
        print "contex", context
        invo_obj = self.pool.get('account.invoice')
        wz_brw = products or ids and self.browse(cr,uid,ids and ids[0],context=context)
        print "wz_brw",wz_brw
        product_True = products or wz_brw.product
        period_id =  products and period or wz_brw and wz_brw.period_id.id
        products = period and products or wz_brw and wz_brw.product_ids
        if product_True:
            dic_comp = {}
            dic_vent = {}
            dic_nc_com = {}
            dic_nc_vent = {}
            aux = {}
            [(dic_comp.update({i.id:[]}),dic_vent.update({i.id:[]})   , dic_nc_com.update({i.id:[]})    , dic_nc_vent.update({i.id:[]})) for i in products]
            
            #~  Select quantity and cost of product from supplier invoice
            invo_com_ids = invo_obj.search(cr,uid,[('invoice_line.product_id','in', tuple(dic_comp.keys())),('type','=','in_invoice'),('period_id','=',period_id)],order='date_invoice')
            
            if invo_com_ids:
                [dic_comp[line.product_id.id].append((invo.id,line.price_unit,line.price_subtotal, line.quantity, line.uos_id and line.uos_id.id))  for invo in invo_obj.browse(cr,uid,invo_com_ids,context=context) for line in invo.invoice_line if line and line.product_id and line.product_id.id in dic_comp and type(dic_comp[line.product_id.id]) is list ]
           
           
            #~ Select quantity and cost of product from customer invoice
            invo_ven_ids = invo_obj.search(cr,uid,[('invoice_line.product_id','in', tuple(dic_vent.keys())),('type','=','out_invoice'),('period_id','=',period_id)],order='date_invoice')
            
            if invo_ven_ids:
                [dic_vent[line.product_id.id].append((invo.id,line.price_unit,line.price_subtotal, line.quantity, line.uos_id and line.uos_id.id))  for invo in invo_obj.browse(cr,uid,invo_ven_ids,context=context) for line in invo.invoice_line if line and line.product_id and line.product_id.id in dic_vent and type(dic_vent[line.product_id.id]) is list ]
          
            #~ Select quantity and cost of product from credit note for a supplier invoice 
            invo_nc_com_ids = invo_obj.search(cr,uid,[('invoice_line.product_id','in', tuple(dic_nc_com.keys())),('type','=','in_refund'),('period_id','=',period_id)],order='date_invoice')
            if invo_nc_com_ids:
                [dic_nc_com[line.product_id.id].append((invo.id,line.price_unit,line.price_subtotal, line.quantity, line.uos_id and line.uos_id.id))  for invo in invo_obj.browse(cr,uid,invo_nc_com_ids,context=context) for line in invo.invoice_line if line and line.product_id and line.product_id.id in dic_nc_com and type(dic_nc_com[line.product_id.id]) is list ]
                
            
            invo_nc_ven_ids = invo_obj.search(cr,uid,[('invoice_line.product_id','in', tuple(dic_nc_vent.keys())),('type','=','out_refund'),('period_id','=',period_id)],order='date_invoice')
            if invo_nc_ven_ids:
                [dic_nc_vent[line.product_id.id].append((invo.id,line.price_unit,line.price_subtotal, line.quantity, line.uos_id and line.uos_id.id))  for invo in invo_obj.browse(cr,uid,invo_nc_ven_ids,context=context) for line in invo.invoice_line if line and line.product_id and line.product_id.id in dic_nc_vent and type(dic_nc_vent[line.product_id.id]) is list ]
           
            print "dic_comp",dic_comp
            print "dic_vent",dic_vent
            print "dic_nc_com",dic_nc_com
            print "dic_nc_vent",dic_nc_vent
           
            for i in dic_comp:
                if dic_comp.get(i,False) and len(dic_comp[i]) > 0:
                    ids_inv = {} 
                    [ids_inv.update({h[0]:h[1]}) for h in dic_comp[i]]
                    if dic_vent.get(i,False) and len(dic_vent.get(i,[])) > 0 :
                        lista = self.list_cost(dic_vent.get(i),ids_inv)
                        dic_vent.update({i:lista}) 
                
                    if dic_nc_vent.get(i,False) and len(dic_nc_vent.get(i,[])) > 0 :
                        lista = self.list_cost(dic_nc_vent[i],ids_inv)
                        dic_nc_vent.update({i:lista}) 
                
                    if dic_nc_com.get(i,False) and len(dic_nc_com.get(i,[])) > 0 :
                        lista = self.list_cost(dic_nc_com[i],ids_inv)
                        dic_nc_com.update({i:lista}) 
                
            for i in dic_comp:
                if dic_comp.get(i,False) and len(dic_comp[i]) > 0:
                    
                    qty = (sum([a[3] for a in dic_comp.get(i)])) - (dic_nc_com.get(i,False) and len(dic_nc_com.get(i)) > 0 and sum([a[0] for a in dic_nc_com.get(i)] or 0)) + (dic_nc_vent.get(i,False) and len(dic_nc_vent.get(i)) > 0 and sum([a[0] for a in dic_nc_vent.get(i)]) or 0) - (dic_vent.get(i,False) and len(dic_vent.get(i)) > 0 and sum([a[0] for a in dic_vent.get(i)]) or 0)
                    
                    
                    price = sum([a[2] for a in dic_comp.get(i)]) - (dic_nc_com.get(i,False) and len(dic_nc_com.get(i)) > 0 and sum([a[1] for a in dic_nc_com.get(i)] or 0)) + (dic_nc_vent.get(i,False) and len(dic_nc_vent.get(i)) > 0 and sum([a[1] for a in dic_nc_vent.get(i)])) - (dic_vent.get(i,False) and len(dic_vent.get(i)) > 0 and sum([a[1] for a in dic_vent.get(i)]) or 0)
                    if qty > 0 :
                        cost = price / qty
                        aux.update({i:[price,qty,cost and cost]})

            dic_comp = aux
            print "dic_comp",dic_comp

        return True
compute_cost()
