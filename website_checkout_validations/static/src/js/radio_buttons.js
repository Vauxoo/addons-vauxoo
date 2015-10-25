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
      var selects = [$("select[name='state_id']"),
                       $("select[name='district_id']"),
                       $("select[name='township_id']"),
                       $("select[name='hood_id']")];
         if ($("select[name=country_id]").find(":selected").attr("id") == 'PA')
         {
          $("div[id=zip]").hide();
          $("div[id=ruc_values]").css('visibility','visible');
          $.each(selects, function(index, select){
            select.parent().toggle(true);
          });
         }
         else{
          $("div[id=ruc_values]").css('visibility','hidden');
          $.each(selects, function(index, select){
            select.parent().toggle(false);
          });
         }
       $("select[name=country_id]").click(function(){
         if ($("select[name=country_id]").find(":selected").attr("id") == 'PA')
         {
          $("div[id=zip]").hide();
          $("div[id=ruc_values]").css('visibility','visible');
          $.each(selects, function(index, select){
            select.parent().toggle(true);
          });
         }
         else
         {
          $("div[id=zip]").show();
          $("div[id=ruc_values]").css('visibility','hidden');
          $.each(selects, function(index, select){
            select.parent().toggle(false);
          });
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
          if ($("#partner_type_c").is(':checked'))
            {
              $("div[id=ruc_values]").css('visibility','visible');
              $("div[id=company]").hide();
              $("label[for=contact_name_partner]").text('Copany Name');
            }
          else{
            $("div[id=company]").hide();
            $("label[for=contact_name_partner]").text('Contact Name');
          }
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
       //JS for billing fields
       $("select[name='state_id']").change(function(){
        var $select = $("select[name='district_id']");
        $select.find("option:not(:first)").hide();
        var nb = $select.find("option[data-state_id="+($(this).val() || 0)+"]").show().size();
        $select.val(0);
        $("select[name='township_id']").val(0);
        $("select[name='hood_id']").val(0);

       });
    $("select[name='state_id']").change();

    $("select[name='district_id']").change(function(){
        var $select = $("select[name='township_id']");
        $select.find("option:not(:first)").hide();
        var nb = $select.find("option[data-district_id="+($(this).val() || 0)+"]").show().size();
        $select.val(0);
        $("select[name='hood_id']").val(0);
       });
    $("select[name='district_id']").change();

    $("select[name='township_id']").change(function(){
        var $select = $("select[name='hood_id']");
        $select.find("option:not(:first)").hide();
        var nb = $select.find("option[data-township_id="+($(this).val() || 0)+"]").show().size();
        $select.val(0);
       });
    $("select[name='township_id']").change();

    //JS for shipping fields

    $("select[name='shipping_state_id']").change(function(){
        var $select = $("select[name='shipping_district_id']");
        $select.find("option:not(:first)").hide();
        var nb = $select.find("option[data-state_id="+($(this).val() || 0)+"]").show().size();
       });
    $("select[name='shipping_state_id']").change();

    $("select[name='shipping_district_id']").change(function(){
        var $select = $("select[name='shipping_township_id']");
        $select.find("option:not(:first)").hide();
        var nb = $select.find("option[data-district_id="+($(this).val() || 0)+"]").show().size();
       });
    $("select[name='shipping_district_id']").change();

    $("select[name='shipping_township_id']").change(function(){
        var $select = $("select[name='shipping_hood_id']");
        $select.find("option:not(:first)").hide();
        var nb = $select.find("option[data-township_id="+($(this).val() || 0)+"]").show().size();
       });
    $("select[name='shipping_township_id']").change();


    },

  });

})();
