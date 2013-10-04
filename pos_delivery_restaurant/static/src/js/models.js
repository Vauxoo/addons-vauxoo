function delivery_restaurant_models(instance, module){
    
    module.PosModel = module.PosModel.extend({
        initialize : function(session, attributes) {
            this._super(session, attributes);
            //this.db.clear('products');
            //this.set({'products':new module.ProductCollection()});
        },
        
        load_server_data : function(){
            self = this;
            loaded = this._super()
                .then(function(){
                    return self.fetch(
                    'pos.config',
                    ['id', 'deli_rest'],
                    [['id','=', self.get('pos_session').config_id[0]]]
                    );
                }).then(function(configs){
                    var pos_config = configs[0];
                    self.set('pos_config', pos_config);
                    console.log(pos_config);
                    
                    if( pos_config.deli_rest == 'delivery'){
                    return self.fetch(
                        'product.product', 
                        ['id','name', 'restaurant' , 'delivery'],
                        [['sale_ok','=',true],['available_in_pos','=',true],['delivery','=',true]]
                        
                        );
                    }
                    else{
                    return self.fetch(
                        'product.product', 
                        ['id','name', 'restaurant' , 'delivery'],
                        [['sale_ok','=',true],['available_in_pos','=',true],['restaurant','=',true]]
                        
                        );
                    }

                }).then(function(products){
                    //this.db.clear('products');
                    //this.set({'products':new module.ProductCollection()});
                    self.db.add_products(products);
                });
            return loaded;
        },

    })

}
