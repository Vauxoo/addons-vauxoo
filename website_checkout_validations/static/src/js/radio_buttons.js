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
       if ($("#partner_type_p").is(':checked'))
        {
          $("div[id=company]").hide();
        }
       $(".partner_type").click(function(){
         var selectedBox = this.id;
         if (this.value == 'particular')
         {
          $("div[id=company]").hide();
         }
         else
         {
          $("div[id=company]").show();
         }

       });

    },

  })

})();
