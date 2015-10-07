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
      // THIS CODE HIDES OR SHOWS THE ZIP IF PANAMA SELECTED OR NOT
         if ($("select[name=country_id]").find(":selected").attr("id") == 'PA')
         {
          $("div[id=zip]").hide();
          $("div[id=ruc_values]").css('visibility','visible');
         }
         else{
          $("div[id=ruc_values]").css('visibility','hidden');
         }
       $("select[name=country_id]").click(function(){
         if ($("select[name=country_id]").find(":selected").attr("id") == 'PA')
         {
          $("div[id=zip]").hide();
          $("div[id=ruc_values]").css('visibility','visible');
         }
         else
         {  
          $("div[id=zip]").show();
          $("div[id=ruc_values]").css('visibility','hidden');
         }
       });
       // THIS CODE HIDES THE COMPANY INPUT IF PARTNER IS PARTICULAR
       if ($("#partner_type_p").is(':checked'))
        {
          $("div[id=ruc_values]").css('visibility','hidden');
          $("div[id=company]").hide();
          $("label[for=contact_name_partner]").text('Contact Name');
        }
        else
        {
          $("div[id=company]").hide();
          $("label[for=contact_name_partner]").text('Copany Name');
        }
       $(".partner_type").click(function(){
         var selectedBox = this.id;
         if (this.value == 'particular')
         {
          $("label[for=contact_name_partner]").text('Contact Name');
          $("div[id=ruc_values]").css('visibility','hidden');
          $("div[id=company]").hide();
         }
         else
         {
          //$("div[id=company]").show();
          $("label[for=contact_name_partner]").text('Copany Name');
          // If is company and is foreign
          if ($("select[name=country_id]").find(":selected").attr("id") == 'PA')
         {
          $("div[id=ruc_values]").css('visibility','visible');
         }
         else
         {
          $("div[id=ruc_values]").css('visibility','hidden');
         }
         }

       });

    },

  })

})();
