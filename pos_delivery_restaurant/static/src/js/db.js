function delivery_restaurant_db(instance, module){
    module.PosLS.include({
    
        init: function(options){
            this._super(options);           
        },

        add_products: function(products){
            this._super(products);
            var self = this;

            for(var i = 0, len = products.length; i < len; i++){
                var product = products[i];
             console.log('hola ' + product.name + product.restaurant); 
        
                
            }     
       },  
    
    })
}
