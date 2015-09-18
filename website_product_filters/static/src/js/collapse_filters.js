(function(){
  'use strict';

  var website = openerp.website;
  website.snippet.animationRegistry.collapseFilters = website.snippet.Animation.extend({
    selector : ".js_attributes",
    start: function(){
      this.redrow();
    },
    // stop: function(){
    //   this.clean();
    // },

    redrow: function(debug){
      // this.clean(debug);
      this.build(debug);
    },

    // clean:function(debug){
    //   this.$target.empty();
    // },

    build: function(debug){
      $(".show-more").click(function(){
        var parent = $(".show-more").parent();
        var button = $(".show-more");
        var hidden_elements = parent.find(".hidden");
        if (button.hasClass("clicked")){
          var shown_elements = parent.find(".un-hidden");
          shown_elements.addClass("hidden");
          shown_elements.removeClass("un-hidden");
          button.html('<a class="show-more"><span class="fa fa-plus-square"></span> Show More</a>');
          button.removeClass("clicked");
        }
        else {
          hidden_elements.removeClass("hidden");
          hidden_elements.addClass("un-hidden");
          button.html('<a class="show-more"><span class="fa fa-minus-square"></span> Show Less</a>');
          button.addClass("clicked");
        }
        });
    },

  })

})();
