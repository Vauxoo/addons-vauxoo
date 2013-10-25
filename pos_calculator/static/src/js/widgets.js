openerp.pos_calculator = function(instance) {
    var module = instance.point_of_sale;

    module.ScreenSelector.include({                                             
        add_popup: function(popup_name, popup){                                 
            popup.hide();                                                       
            this.popup_set[popup_name] = popup;                                 
            return this;                                                        
        },                                                                      
    });
                                                                                
    module.PosWidget.include({                                                  
        build_widgets: function() {                                             
            var self = this;                                                       
            this._super();                                                         
            this.calculator_ticket = new module.CalculatorPopup(this, {});                 
            this.calculator_ticket.appendTo($('.point-of-sale'));                  
            this.screen_selector.add_popup('calculator-ticket',this.calculator_ticket);
        },                                                                         
    });                                                                            
                                                                                   
    module.BasePopup = module.PopUpWidget.extend({
        template:"BasePopup",                                                      
        renderElement:function(){                                                  
            this._super();                                                         
            this.$("a.close").off('click').click(_.bind(this.closePopup,this))  
        },                                                                         
        closePopup:function(e){                                                    
            this.close();                                                          
            this.hide();                                                           
        },                                                                         
                                                                                   
    }); 

    module.CalculatorPopup = module.BasePopup.extend({                          
        template:"CalculatorPopup",                                             
        events:{                                                                
            "click button[name='cancel']":"onCancelBtn",                                        
            "click button[name='save']":"onClickBtn",                           
            "click button[id='numpad-backspace']":"onClickBack",                
            "click .input-button":"onClickCalc",                                
            "click .ondiv":"onClickOut",                                
            "keydown input[id='capturekey']":"onKeyPressI",
        },                                                                      
        init: function(parent, options){                                        
            this.id="calculator-ticket";                                        
            this.title = "Calculator";                                          
            this._super(parent, options);                                       
        },                                                                      
        show: function(){                                                       
            this._super();                                                      
            this.cleanInput();
            this.$("input[id='capturekey']")[0].focus();
        },  
        cleanInput: function() {
            this.amount = "";                                                   
            this.lastKey = "";
            this.subtotal = "0.00";                                             
            this.decimalAdded = false;                                               
            this.pressResult = false;                                                
            this.$(".amount-input")[0].textContent = "";                        
        },
        closePopup: function(e){
            this.cleanInput();
            $(this.elem).focus();
            this._super(e);
        },
        onCancelBtn: function(e){                                                
            this.cleanInput();
            $(this.elem).focus();                                               
            this.close();                                                       
            this.hide();                                                        
        },                                                                      
        onClickOut: function(e){
            this.$("input[id='capturekey']")[0].focus();
        },
        onClickBack: function(e){                                               
            this.cleanInput();
        },                                                                      
        onKeyPressI: function(e){
            var caracter = e.charCode || e.keyCode;
            var keyp = "";
            var namekey = "";
            switch(caracter)
            {
                case 8: keyp = "numpad-backspace"; break;
                case 13: keyp = "key-equal"; break;
                case 27: keyp = "cancel"; break;
                case 32: keyp = "save"; break;
                case 46: keyp = "numpad-backspace"; break;
                case 106: keyp = "key-multiply"; break;
                case 107: keyp = "key-plus"; break;
                case 109: keyp = "key-minus"; break; 
                case 110: keyp = "key-dot"; break;
                case 111: keyp = "key-divide"; break;
                case 189: keyp = "key-minus"; break;
                case 190: keyp = "key-dot"; break;
                case 191: keyp = "key-divide"; break;
                default: if (caracter >= 48 && caracter <= 57)  
                        keyp = "key-" + String.fromCharCode(caracter); break;
            }
            namekey = "#"+ keyp;
            if (keyp) { 
                this.$(namekey).click();
            }
        },
        onClickBtn: function(e){                                                
            if (this.$(".amount-input")[0].textContent != "") {
                this.pos_widget.payment_screen.currentPaymentLines.last().set_amount(this.subtotal);
                this.$(".amount-input")[0].textContent = "";
            }                 
            this.cleanInput();
            $(this.elem).focus();                                               
            this.close();                                                       
            this.hide();                                                        
        },     
       onClickCalc: function(e){                                               
            var operators = ['+', '-', 'x', '÷'];                                           
            var inputVal = this.$(".amount-input")[0].textContent;              
            var btnVal = e.currentTarget.innerText;                             
            if(btnVal == 'C') {                                                     
                this.cleanInput();
                this.lastKey = "C";
            }                                                                   
            else if(btnVal == '=') {                                            
                var equation = inputVal;                                            
                var lastChar = equation[equation.length - 1];                       
                equation = equation.replace(/x/g, '*').replace(/÷/g, '/');          
                if(operators.indexOf(lastChar) > -1 || lastChar == '.')             
                    equation = equation.replace(/.$/, '');                          
                if(equation){                                                        
                    this.$(".amount-input")[0].textContent = eval(equation);                               
                    this.$("#equation-calc").text(equation);
                }
                this.pressResult = true;                                             
                this.lastKey = "=";
            }                                                                   
            else if(operators.indexOf(btnVal) > -1) {                           
                var lastChar = inputVal[inputVal.length - 1];                       
                if(inputVal != '' && operators.indexOf(lastChar) == -1)             
                    this.$(".amount-input")[0].textContent += btnVal;                                      
                else if(inputVal == '' && btnVal == '-')                            
                    this.$(".amount-input")[0].textContent += btnVal;                                      
                if(operators.indexOf(lastChar) > -1 && inputVal.length > 1) {       
                    this.$(".amount-input")[0].textContent = inputVal.replace(/.$/, btnVal);               
                }                                                                   
                this.decimalAdded = false;                                            
            }                                                                   
            else if(btnVal == '.') {                                                
                if(!this.decimalAdded) {                                                 
                    this.$(".amount-input")[0].textContent += btnVal;                                      
                    this.decimalAdded = true;                                            
                }                                                                   
            }                                                                       
            else {                                                                  
                this.$(".amount-input")[0].textContent += btnVal;                                          
            }                                                                       
            e.preventDefault();                                                 
            this.amount = this.$(".amount-input")[0].textContent;               
            if (this.pressResult) {                                                  
                this.subtotal = this.amount;                                    
                this.pressResult = false;                                            
            }
            this.$("input[id='capturekey']")[0].focus();
        },                                                                      
    });

    module.PaymentScreenWidget = module.PaymentScreenWidget.extend({
        show: function(){                                                           
            this._super();                                                          
            var self = this;                                                    
            this.calc_button = this.add_action_button({                         
                    label: instance.web._t('Calculator'),                                              
                    icon: '/pos_calculator/static/src/img/icons/Calculator48x48.png',
                    click: function(){                                              
                        console.log("show calculator");                                      
                        self.pos_widget.screen_selector.show_popup('calculator-ticket');
                    },                                                              
                });                                                             
           },
    });

};
