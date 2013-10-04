function delivery_restaurant_widgets(instance, module){
    module.ProductCategoriesWidget.include({
        search_and_categories: function(category){
            this._super(category);
            self = this;
          },

    })
}

