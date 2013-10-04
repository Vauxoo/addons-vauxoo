function delivery_restaurant_db(instance, module){
    module.PosLS.include({
    
        init: function(options){
            this._super(options);           
        },

        add_products: function(products){
            this._super(products);
            var self = this;

          for(var i = 0, len = products.length; i < len; i++){
            var prod = products[i];
            console.log('product_by:');
            console.log(this.product_by_id[prod.id]); 
                
            }     
       },  
    
    })
}
            

/*this.product_by_id[prod.id].restaurant =
            prod.restaurant;
            this.product_by_id[prod.id].delivery = prod.delivery;
          */
                                                             
            
             
             /*
                        _.filter(products, function(prod){            
                var res_or_del = self.pos.get('pos_config').deli_rest;                              
                     console.log(prod); 
                 if( (res_or_del === 'restaurant' && prod.restaurant == true) ){
                     console.log(this.product_by_id[prod.id]); 
                     return true;                                                                    
                 }                     
                 if( (res_or_del === 'delivery' && prod.delivery == true) ){                         
                     console.log(this.product_by_id[prod.id]); 
                     return true;                                                                    
                 }                                                                                   
                 return false;
                 });*/
