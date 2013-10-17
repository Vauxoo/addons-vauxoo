function delivery_restaurant_models(instance, module){
    
    module.PosModel = module.PosModel.extend({
        initialize : function(session, attributes) {
            this._super(session, attributes);
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
                    //Se reciben los productos dependiento si el
                    //pos es delivery o restaurant
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
                    self.db.add_products(products);
                });
            return loaded;
        },

    })

}
