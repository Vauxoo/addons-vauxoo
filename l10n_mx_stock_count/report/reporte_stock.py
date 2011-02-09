# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Angelica Barrios angelicaisabelb@gmail.com
#              Humberto Arocha humberto@openerp.com.ve
#    Planified by: Humberto Arocha
#    Finance by: LUBCAN COL S.A.S http://www.lubcancol.com
#    Audited by: Humberto Arocha humberto@openerp.com.ve
#############################################################################
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
##############################################################################

import time
from report import report_sxw
from osv import osv
import pooler

class rep_conteo_stock(report_sxw.rml_parse):
    


    def __init__(self, cr, uid, name, context):
        super(rep_conteo_stock, self).__init__(cr, uid, name, context)    
        self.localcontext.update({
            'time': time                                ,
            'get_data':self.get_data                    ,
            'get_tipo':self.get_tipo                    ,
            'get_category':self.get_category            ,
            'get_state':self.get_state                  ,
            'get_destinado':self.get_destinado          ,
            'get_suministro':self.get_suministro        ,
            'get_qty_available':self.get_qty_available  ,
            'get_code':self.get_code                    ,
        })



    def get_tipo(self, stock=None):
        product= self.pool.get('product.template')
        cabeza=[]
        boole=False
        if stock.tipo=="almacenable" or stock.tipo=="consumible": 
            cabeza.append("Almacenable/Consumible")
            boole=True
        if stock.tipo=="servicio":
            cabeza.append("Servicio")
            boole=True
        if boole==False:
            cabeza.append("Almacenable - Consumible / Servicio")
        return cabeza    
            
    def get_category(self, stock=None):
        product= self.pool.get('product.template')
        cabeza=[]
        if stock.categoria:
            cabeza.append(" %s"%(stock.categoria.name))
        else:
            cabeza.append("Todas las Categorias") 
        return cabeza 
    
    def get_state(self, stock=None):
        product= self.pool.get('product.template')
        cabeza=[]       
        if stock.estado:
            cabeza.append(" %s"%(stock.estado))
        else:
            cabeza.append("Todas los Estados")
        return cabeza
    
    def get_destinado(self, stock=None):
        product= self.pool.get('product.template')
        cabeza=" "
        
        if stock.vendible:
            cabeza="Vendible " 
            
        if stock.comprable:
            cabeza =cabeza+" Comprable"

        if stock.alquilable:
            cabeza=cabeza + "Alquilable"

        if not stock.vendible and not stock.comprable and not stock.alquilable:
            cabeza="Vendible Comprable Alquilable"
        return cabeza
    
    def get_suministro(self, stock=None):
        product= self.pool.get('product.template')
        cabeza=[]
        if stock.suministro:
            cabeza.append(" %s"%(stock.suministro))
        else:
            cabeza.append("Todas los Tipos de Suministro")      
        return cabeza
     
    
    
    def get_data (self,stock=None ):
        print"Entro al metodo get_data"
        product= self.pool.get('product.template')
        merge=[]
        ##################para el tipo del producto####################
        
        if stock.tipo=="almacenable": 
            merge.append( ('type', '=',"product"))  
        if stock.tipo=="consumible": 
            merge.append( ('type', '=',"consut"))
        if stock.tipo=="servicio":
             merge.append( ('type', '=',"service") ) 
        
        ##################para la categoria####################

        if stock.categoria:
            merge.append( ('categ_id', '=',stock.categoria.id) ) 
            
        ##################para el estado####################
        if stock.estado:
            if stock.estado=="desarrollo":
                merge.append( ('state', '=',"draft") ) 
                
            if stock.estado=="produccion":
                merge.append( ('state', '=',"sellable") ) 

            if stock.estado=="fin":
                merge.append( ('state', '=',"end") )

            if stock.estado=="obsoleto":
                merge.append( ('state', '=',"obsolete") )
  
            if stock.estado=="none":
                merge.append( ('state', '=',None) )
                
        ##################destinado a ser: vendible, conyable, alquilable####################
        if stock.vendible:
            merge.append( ('sale_ok', '=',True) )

        if stock.comprable:
            merge.append( ('purchase_ok', '=',True) )

        if stock.alquilable:
            merge.append( ('rental', '=',True) )
            
        ##################tipo de suministro####################

        if stock.suministro=="comprar":
            merge.append( ('supply_method', '=','produce') )
            
        if stock.suministro=="producir":
            merge.append( ('supply_method', '=','buy') )

        print "el MERGE ES:", merge
        id_productos=product.search(self.cr, self.uid, merge, order="name" )
        print "los ids son: ",id_productos
        data =product.browse(self.cr,self.uid, id_productos) #lista de product_template que cumplen la condicion
        return data


    def get_qty_available (self,id_template ):
        qty=0.0
        qty2=0.0
        product= self.pool.get('product.product')
        try:
            id_producto=product.search(self.cr, self.uid, [('product_tmpl_id', '=',id_template.id)])
            producto=product.browse(self.cr,self.uid, id_producto[0])
            qty=producto.qty_available
            qty2=producto.virtual_available
            res=[qty,qty2]
            return res
        except:
            res=[qty,qty2]
            return res

    def get_code(self,id_template):
        code="-"
        product= self.pool.get('product.product')
        try:
            id_producto=product.search(self.cr, self.uid, [('product_tmpl_id', '=',id_template.id)])
            producto=product.browse(self.cr,self.uid, id_producto[0])
            code=producto.code
            return code
        except:
            return code














    
#    def get_encabezado(self, stock=None):
#        product= self.pool.get('product.template')
#        cate= self.pool.get('product.category')
#        cabeza=[]
#        if stock.almacenable_consumible==True:
#            cabeza.append("Almacenable/Consumible")
#        else:
#            cabeza.append(" ")   
#        if stock.servicio==True:
#            cabeza.append("Servicio")
#        else:
#            cabeza.append(" ") 
#        if not stock.almacenable_consumible==True and not stock.servicio==True:
#            cabeza[0]="Almacenable/Consumible"
#            cabeza[1]="Servicio"
#       
#    
#        if stock.categoria:
#            cabeza.append(" %s"%(stock.categoria.name))
#        else:
#            cabeza.append("Todas las Categorias") 
#       
#        if stock.estado:
#            cabeza.append(" %s"%(stock.estado))
#        else:
#            cabeza.append("Todas los Estados")
#        
#        if stock.vendible:
#            cabeza.append("Vendible")
#        else:
#            cabeza.append(" ")
#        if stock.comprable:
#            cabeza.append("Comprable")
#        else:
#            cabeza.append(" ")
#        if stock.alquilable:
#            cabeza.append("Alquilable")
#        else:
#            cabeza.append(" ")
#        if not stock.vendible and not stock.comprable and not stock.alquilable:
#            cabeza[4]="Vendible"
#            cabeza[5]="Comprable"
#            cabeza[6]="Alquilable" 
#              
#        print cabeza
#        
#        return cabeza
#    
#    
#    def get_data (self,stock=None ):
#        print"Entro al metodo get_data"
#        print "el estado es: ",stock.estado
#        product= self.pool.get('product.template')
#        
#        ##################para el tipo del producto####################
#        tipo=[]
#        if stock.almacenable_consumible==True:
#            stock_pro = product.search(self.cr, self.uid, [('type', '=',"product")])
#            tipo.extend(stock_pro)

#        if stock.servicio==True:
#            stock_serv = product.search(self.cr, self.uid, ['|',('type', '=',"consut"),('type', '=',"service")]) 
#            tipo.extend(stock_serv)

#        #sin repetisiones obtengo los tipos de productos
#        sin_repetir_tipo=[x for x in set(tipo)]
#        
#        if not sin_repetir_tipo: #si esta vacia
#            sin_repetir_tipo=product.search(self.cr, self.uid, [])
#        
#        print "sin_repetir_tipo: ",sin_repetir_tipo 
#        
#        ##################para la categoria####################
#        stock_category=[]
#        if stock.categoria:
#            stock_category = product.search(self.cr, self.uid, [('categ_id', '=',stock.categoria.id)])

#        else: #dame todos
#            stock_category = product.search(self.cr, self.uid, [])
#        if not stock_category:
#            stock_category = product.search(self.cr, self.uid, [])
#            
#        print "stock_category: ",stock_category
#            
#            
#            
#        ##################para el estado####################
#        stock_estado=[]
#        if stock.estado:
#            if stock.estado=="desarrollo":
#                stock_estado = product.search(self.cr, self.uid, [('state', '=',"draft")])
#                
#            if stock.estado=="produccion":
#                stock_estado = product.search(self.cr, self.uid, [('state', '=',"sellable")])

#            if stock.estado=="fin":
#                stock_estado = product.search(self.cr, self.uid, [('state', '=',"end")])

#            if stock.estado=="obsoleto":
#                stock_estado = product.search(self.cr, self.uid, [('state', '=',"obsolete")])
#  
#            if stock.estado=="none":
#                stock_estado = product.search(self.cr, self.uid, [('state', '=',None)])

#        else:
#            stock_estado = product.search(self.cr, self.uid, [])
#        if not stock_estado:
#            stock_estado = product.search(self.cr, self.uid, [])
#        
#        print "stock_estado: ",stock_estado
#            
#                
#        ##################destinado a ser: vendible, conyable, alquilable####################
#        destino=[]
#        if stock.vendible:
#            stock_ven=product.search(self.cr, self.uid, [('sale_ok', '=',True)])
#            destino.extend(stock_ven)

#        if stock.comprable:
#            stock_comp=product.search(self.cr, self.uid, [('purchase_ok', '=',True)])
#            destino.extend(stock_comp)

#        if stock.alquilable:
#            stock_alq=product.search(self.cr, self.uid, [('rental', '=',True)])
#            destino.extend(stock_alq)
#        #sin repetisiones obtengo los tipos de productos
#        sin_repetir_destino=[x for x in set(destino)] 
#        if not sin_repetir_destino:
#            sin_repetir_destino=product.search(self.cr, self.uid, [])  
#        print "sin_repetir_destino: ",sin_repetir_destino
#        
##se une todas las intersecciones de los filtros para los productos
#        ids_product_template=list(set(sin_repetir_tipo)&set(stock_category)&set(stock_estado)&set(sin_repetir_destino))
#        print "TOTALLLLLLLLL:",ids_product_template
#        
#        data =product.browse(self.cr,self.uid, ids_product_template)
#        
#        return data

#    def get_code(self,id_template):
#        code="-"
#        product= self.pool.get('product.product')
#        try:
#            id_producto=product.search(self.cr, self.uid, [('product_tmpl_id', '=',id_template.id)])
#            producto=product.browse(self.cr,self.uid, id_producto[0])
#            code=producto.code
#            return code
#        except:
#            return code
      
report_sxw.report_sxw(
    'report.hoja.conteo.stock'                              ,  
    'stock.count'                                           ,
    'addons/l10n_co_stock_count/report/hoja_conteo.rml'     ,  
    parser=rep_conteo_stock                                 ,
)      
