(function(){
  'use strict';

  var website = openerp.website;
  website.snippet.animationRegistry.checkoutValidations = website.snippet.Animation.extend({
    selector : ".partner_type",
    start: function(){
      this.redrow();
    },
    stop: function(){
      this.clean();
    },

    redrow: function(debug){
      this.clean(debug);
      this.build(debug);
    },

    clean:function(debug){
      this.$target.empty();
    },

    build: function(debug){
       console.log("enters");
       $(".partner_type").click(function(){

         var selectedBox = this.id;
         console.log(this.id);
         console.log(selectedBox);
       });

    },

  })

})();
