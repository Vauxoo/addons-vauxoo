function delivery_restaurant_models(instance, module){
    
    module.PosModel = module.PosModel.extend({
        initialize : function(session, attributes) {
            this._super(session, attributes);
            console.log('hola estoy en ini');
            //this.db.clear('products');
            //this.set({'products':new module.ProductCollection()});
        },
        
        load_server_data : function(){
            self = this;
            loaded = this._super()
                .then(function(){
                    return self.fetch(
                    'pos.config',
                    ['deli_rest'],
                    [['id','=', self.get('pos_session').config_id[0]]]
                    );
                }).then(function(configs){
                    var pos_config = configs[0];
                    self.set('pos_config', pos_config);
                    return self.fetch(
                        'product.product', 
                        ['restaurant' , 'delivery'],
                        [['sale_ok','=',true],['available_in_pos','=',true]]
                        
                        );
                }).then(function(products){
                    //this.db.clear('products');
                    //this.set({'products':new module.ProductCollection()});
                    console.log("Hola");
                    self.db.add_products(products);
                });
            return loaded;
        },

    })

}
