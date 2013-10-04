function delivery_restaurant_widgets(instance, module){
    module.ProductCategoriesWidget.include({
        search_and_categories: function(category){
            this._super();
            self = this;
/*           
            var products = this.pos.db.get_product_by_category(this.category.id);
            
            console.log( "hola " + this.pos.get('pos_config').deli_rest );
            //console.log('hola extend');
            //var products = this.pos.get('products');
            //console.log( products);

             products = _.filter(products, function(prod){            
                 var res_or_del = self.pos.get('pos_config').deli_rest;                              
            //        console.log( prod.name );
                 if( (res_or_del === 'restaurant' && prod.restaurant == true) ||                     
                     (res_or_del === 'delivery' && prod.delivery == true) ){                         
                     return true;                                                                    
                 }                                                                                   
                 return false;                                                                       
             });
  
          self.pos.get('products').reset(products);
         */
          },

    })
}

