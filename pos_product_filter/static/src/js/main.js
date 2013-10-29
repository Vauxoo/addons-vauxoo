openerp.pos_delivery_restaurant = function(instance){
    var module = instance.point_of_sale;
    delivery_restaurant_models(instance,module);
    instance.pos_delivery_restaurant = module;
}
