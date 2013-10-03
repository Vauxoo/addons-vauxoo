openerp.delivery_restaurant = function(instance){
    var module = instance.point_of_sale;
    delivery_restaurant_models(instance,module);
    //delivery_restaurant_widgets(instance,module); 
    instance.delivery_restaurant = module;
}
