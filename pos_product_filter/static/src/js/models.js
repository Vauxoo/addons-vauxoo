function delivery_restaurant_models(instance, module){    
    module.PosModel = module.PosModel.extend({              
        fetch: function(model, fields, domain, ctx){
            if (model == 'pos.config'){
                fields.push('deli_rest');
            }else if (model == 'product.product'){
                var deli_rest = this.get('pos_config').deli_rest;
                if (deli_rest == 'restaurant')
                    domain.push(['restaurant','=',true]);
                else if (deli_rest == 'delivery')
                    domain.push(['delivery','=',true])
            }
            return new instance.web.Model(model).query(fields).filter(domain).context(ctx).all();
        },
    });
}
