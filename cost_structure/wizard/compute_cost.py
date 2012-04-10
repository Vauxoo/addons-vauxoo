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
from DateTime import DateTime
import time

invo_cost = {}

class compute_cost(osv.osv_memory):

    
    _name = 'compute.cost'
    _columns = {
        'product_ids':fields.many2many('product.product','product_rel','product1','product2','Product',help="Select the product to compute cost"),
        'product':fields.boolean('Product',help="To select compute by product"),
        'categ':fields.boolean('Category',help="To select compute by category"),
        'bolfili':fields.boolean('Boolean FIFO LIFO'),
        'categ_ids':fields.many2many('product.category','categ_rel','categ1','categ2','Product Category',help="Select the category to compute cost"),
        'fiscalyear_id':fields.many2one('account.fiscalyear','Fiscal Year',help="Fiscal Year to search invoice between indicated period"),
        'period_id':fields.many2one('account.period','Period',help="Period to search invoice between indicated period"),
        'all':fields.boolean('ALL',help="To compute cost for all products"),
        'fifo':fields.boolean('FIFO',help="To compute cost FIFO for products"),
        'lifo':fields.boolean('LIFO',help="To compute cost LIFO for products"),
        
    }
    
    
    def compute_cost_fifo(self,cr,uid,dic_comp,dic_vent,dic_nc_com,dic_nc_vent,context={}):
        invoice_obj = self.pool.get('account.invoice')
        rec_com = {}
        rec_vent = {}
        [rec_com.update({invoice_obj.browse(cr,uid,e[-1],context=context).parent_id.id:e[0]}) for i in dic_nc_com for e in dic_nc_com.get(i)]
        [rec_vent.update({invoice_obj.browse(cr,uid,h[-1],context=context).parent_id.id:h[0]}) for g in dic_nc_vent for h in dic_nc_vent.get(g)]
        cont = 0
        cont_qty = 0
        price = 0
        for i in dic_comp:
            aux = (d for d in dic_comp.get(i,False))
            try:
                fifo = aux and aux.next()
            except:
                raise osv.except_osv(_('Invalid action !'),_("Impossible to calculate FIFO not have invoices in this period  "))
            qty_aux = fifo and fifo[0] in rec_com.keys() and fifo[3] - rec_com.get(fifo[0],False) or fifo[3]
            cost_aux = fifo and fifo[1]
            
            for d in dic_vent.get(i):
                #~ print "dic_comp[i]",dic_comp[i]
                print "d[0]",d[0]
                print "d[-1]",d[-1]
                print "rec_vent.keys()",rec_vent.keys()
                cont = d[-1] in rec_vent.keys() and (cont + d[0]) - rec_vent.get(d[-1],False) or cont + d[0]
                
                if cont <= qty_aux:
                    price = (d[0] * cost_aux) + price
                else:
                    rest = cont - d[0]
                    rest = qty_aux - cont
                    price = rest > 0 and (rest * cost_aux) + price
                    fifo = aux.next()
                    cont_qty = cont + cont_qty
                    cont = 0
                    qty_aux = fifo and fifo[0] in rec_com.keys() and fifo[3] - rec_com.get(fifo[0],False) or fifo[3]
                    cost_aux = fifo and fifo[1]
        if price and cont_qty or cont:
            print "price",price
            print "cont_qty",(cont_qty > 0  and cont_qty or cont > 0 and cont)
            
            cost = price / (cont_qty > 0  and cont_qty or cont > 0 and cont)
            print "costcostcostcost",cost
        return True
    
    def compute_actual_cost(self,cr,uid,ids,dic_comp,dic_vent,dic_nc_com,dic_nc_vent,context={}):
        product_obj = self.pool.get('product.product')
        aux = {}
        for i in dic_comp:
            if dic_comp.get(i,False) and len(dic_comp[i]) > 0:
                #~ print [a[2] for a in dic_comp.get(i)]
                #~ print [a[1] for a in dic_nc_com.get(i)]
                #~ print [a[1] for a in dic_nc_vent.get(i)]
                #~ print [a[1] for a in dic_vent.get(i)]
                qty = (sum([a[3] for a in dic_comp.get(i)])) - \
                      (sum([a[0] for a in dic_nc_com.get(i)])) + \
                      (sum([a[0] for a in dic_nc_vent.get(i)])) - \
                      (sum([a[0] for a in dic_vent.get(i)]))
                      
                price = (sum([a[2] for a in dic_comp.get(i)])) - \
                        (sum([a[1] for a in dic_nc_com.get(i)])) + \
                        (sum([a[1] for a in dic_nc_vent.get(i)])) - \
                        (sum([a[1] for a in dic_vent.get(i)]))
                
                if qty > 0 :
                    cost = price / qty
                    aux.update({i:[price,qty,cost and cost,dic_comp[i] and dic_comp[i][0] and dic_comp[i][0][4] or [] ]})
                    product_brw = product_obj.browse(cr,uid,i,context=context)
                    
                    if product_brw.property_cost_structure and product_brw.cost_ult > 0:
                        product_obj.write(cr,uid,[product_brw.id],{'cost_ult':cost,'date_cost_ult':time.strftime('%Y-%m-%e').replace(' ','') , 'cost_ant':product_brw.cost_ult ,'date_cost_ant':product_brw.date_cost_ult ,'ult_om':aux.get(i)[-1] or [] ,'date_ult_om': time.strftime('%Y-%m-%e').replace(' ','') , 'ant_om':product_brw.ult_om and product_brw.ult_om.id or [],'date_ant_om':product_brw.date_ult_om },context=context)
                    else:
                        product_obj.write(cr,uid,[product_brw.id],{'cost_ult':cost,'date_cost_ult':time.strftime('%Y-%m-%e').replace(' ',''),'ult_om':aux.get(i)[-1] or [] ,'date_ult_om': time.strftime('%Y-%m-%e').replace(' ','') },context=context)
        return aux
        
        
    def list_cost(self,cr,uid,cicle,ids_inv):
        global invo_cost
        lista = []
        invoice_obj = self.pool.get('account.invoice')
        product_obj = self.pool.get('product.product')
        #~ product_brw = product_obj.browse(cr,uid,[ i for i in ids_inv],context={})
        #~ print "product_brw",product_brw 
        for d in cicle:
            invo_brw = invoice_obj.browse(cr,uid,d[0],context={})
            if invo_brw.type is 'out_refund' and invo_brw.parent_id and invo_brw.parent_id.id in invo_cost:
                lista.append((d[3], d[3] * invo_cost.get(invo_brw.parent_id.id), invo_cost.get(invo_brw.parent_id.id) or 0, d[4],d[0] ))
                return lista
            for date in ids_inv:
                date1 = DateTime(date)
                date2 = DateTime(d[5])
                if date2 >= date1:
                    cost = ids_inv[date]
                    break
            try:
                lista.append((d[3], d[3] * cost, cost and cost or 0, d[4],d[0] ))
            except:
                raise osv.except_osv(_('Invalid action !'),_("Impossible to calculate the actual cost, because the invoice '%s' \
                                                             does not have a valid date format, to place its cost at \
                                                             the time of sale ")% (invo_brw.name))
            if invo_brw.type is 'out_invoice':
                invo_cost.update({d[0]:cost})
        return lista
    
    #~ TODO EL mismo algoritmo para LIFO,
    #~  ""  "" FIFO, 
    #~ meter el concepto de ajuste de inventario
    #~  meter concepto de produccion
    
    def compute_cost(self,cr,uid,ids,context=None,products=False,period=False,fifo=False,lifo=False):
        '''
        Method to compute coste from porduct invoice from a wizard or called from other method
        
        @param products IDS list of products to compute cost from invoices
        @param period ids of period to give range to compute cost 
        @param ids ids of wizard for method call 
        @param fifo booblean to compute cost method fifo
        @param lifo booblean to compute cost method lifo
        '''
        if context is None:
            context = {}
        invo_obj = self.pool.get('account.invoice')
        global invo_cost
        cost_obj = self.pool.get('cost.structure')
        wz_brw = products or ids and self.browse(cr,uid,ids and ids[0],context=context)
        product_True = products or wz_brw.product
        period_id =  products and period or wz_brw and wz_brw.period_id.id
        products = period and products or wz_brw and wz_brw.product_ids
        fifo_true = fifo or wz_brw.fifo
        lifo_true = lifo or wz_brw.lifo
        company_id = self.pool.get('res.users').browse(cr,uid,[uid],context=context)[0].company_id.id
        if product_True:
            dic_comp = {}
            dic_vent = {}
            dic_nc_com = {}
            dic_nc_vent = {}
            
            [(dic_comp.update({i.id:[]}),dic_vent.update({i.id:[]})   , dic_nc_com.update({i.id:[]})    , dic_nc_vent.update({i.id:[]})) for i in products]
            
            #~  Select quantity and cost of product from supplier invoice
            invo_com_ids = invo_obj.search(cr,uid,[('invoice_line.product_id','in', tuple(dic_comp.keys())),
                                                    ('type','=','in_invoice'),
                                                    ('period_id','=',period_id),
                                                    ('company_id','=',company_id)],
                                                    order='date_invoice')
            
            if invo_com_ids:
                [dic_comp[line.product_id.id].append((invo.id,line.price_unit,line.price_subtotal, line.quantity, line.uos_id and line.uos_id.id,invo.date_invoice)) \
                for invo in invo_obj.browse(cr,uid,invo_com_ids,context=context) for line in invo.invoice_line if line and \
                line.product_id and \
                line.product_id.id in dic_comp and \
                type(dic_comp[line.product_id.id]) is list ]
           
            #~ Select quantity and cost of product from customer invoice
            invo_ven_ids = invo_obj.search(cr,uid,[('invoice_line.product_id','in', tuple(dic_vent.keys())),
                                                    ('type','=','out_invoice'),
                                                    ('period_id','=',period_id),
                                                    ('company_id','=',company_id)],
                                                    order='date_invoice')
            
            if invo_ven_ids:
                [dic_vent[line.product_id.id].append((invo.id,line.price_unit,line.price_subtotal, line.quantity, line.uos_id and line.uos_id.id,invo.date_invoice)) \
                for invo in invo_obj.browse(cr,uid,invo_ven_ids,context=context) for line in invo.invoice_line if line and \
                line.product_id and \
                line.product_id.id in dic_vent and \
                type(dic_vent[line.product_id.id]) is list ]
          
            #~ Select quantity and cost of product from credit note for a supplier invoice 
            invo_nc_com_ids = invo_obj.search(cr,uid,[('invoice_line.product_id','in', tuple(dic_nc_com.keys())),
                                                        ('type','=','in_refund'),
                                                        ('period_id','=',period_id),
                                                        ('company_id','=',company_id)],
                                                        order='date_invoice')
            if invo_nc_com_ids:
                [dic_nc_com[line.product_id.id].append((invo.id,line.price_unit,line.price_subtotal, line.quantity, line.uos_id and line.uos_id.id,invo.date_invoice)) \
                for invo in invo_obj.browse(cr,uid,invo_nc_com_ids,context=context) for line in invo.invoice_line if line and \
                line.product_id and \
                line.product_id.id in dic_nc_com and \
                type(dic_nc_com[line.product_id.id]) is list ]
                
            
            invo_nc_ven_ids = invo_obj.search(cr,uid,[('invoice_line.product_id','in', tuple(dic_nc_vent.keys())),
                                                        ('type','=','out_refund'),
                                                        ('period_id','=',period_id),
                                                        ('company_id','=',company_id)],
                                                        order='date_invoice')
            if invo_nc_ven_ids:
                [dic_nc_vent[line.product_id.id].append((invo.id,line.price_unit,line.price_subtotal, line.quantity, line.uos_id and line.uos_id.id,invo.date_invoice)) \
                for invo in invo_obj.browse(cr,uid,invo_nc_ven_ids,context=context) for line in invo.invoice_line if line and \
                line.product_id and \
                line.product_id.id in dic_nc_vent and \
                type(dic_nc_vent[line.product_id.id]) is list ]
           
            
            print "dic_comp1",dic_comp
            print "dic_vent1",dic_vent
            print "dic_nc_com1",dic_nc_com
            print "dic_nc_vent1",dic_nc_vent
            
            
            for i in dic_comp:
                if dic_comp.get(i,False) and len(dic_comp[i]) > 0:
                    ids_inv = {} 
                    [ids_inv.update({h[5]:h[1]}) for h in dic_comp[i]]
                    if dic_vent.get(i,False) and len(dic_vent.get(i,[])) > 0 :
                        lista = self.list_cost(cr,uid,dic_vent.get(i),ids_inv)
                        dic_vent.update({i:lista}) 
                
                    if dic_nc_vent.get(i,False) and len(dic_nc_vent.get(i,[])) > 0 :
                        lista = self.list_cost(cr,uid,dic_nc_vent[i],ids_inv)
                        dic_nc_vent.update({i:lista}) 
                    
                    if dic_nc_com.get(i,False) and len(dic_nc_com.get(i,[])) > 0 :
                        lista = self.list_cost(cr,uid,dic_nc_com[i],ids_inv)
                        dic_nc_com.update({i:lista})
                        
            invo_cost = {}
            if fifo_true or lifo_true:
                fifo = self.compute_cost_fifo(cr,uid,dic_comp,dic_vent,dic_nc_com,dic_nc_vent)
            
            #~ print "dic_comp",dic_comp
            #~ print "dic_vent",dic_vent
            #~ print "dic_nc_com",dic_nc_com
            #~ print "dic_nc_vent",dic_nc_vent
            cost = self.compute_actual_cost(cr,uid,ids,dic_comp,dic_vent,dic_nc_com,dic_nc_vent)
            print "cost",cost

        return True
compute_cost()


    # nombre del modulo account_anglo_saxon_cost_structure 

#~ acttion_cancel asiento (acount_move)
#~ action_move_create (account_invoice)

