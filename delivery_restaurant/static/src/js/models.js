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
                    ['deli_rest'],
                    [['id','=', 
                    self.get('pos_session').config_id[0]]]
                    );
                }).then(function(){
                    return self.fetch(
                        'product.product', 
                        ['restaurant' , 'delivery'],
                        [['sale_ok','=',true],['available_in_pos','=',true]]
                        
                        );
                });
            return loaded;
        },

    })

}
