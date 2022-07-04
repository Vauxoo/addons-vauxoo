/**
 * Refers to vauxoo task#57812 to more information.
 */
odoo.define('villagroup.ClosePosPopup', require => {
    const ClosePosPopup = require('point_of_sale.ClosePosPopup');
    const Registries = require('point_of_sale.Registries');

    const ClosePosPopupInherit = _ClosePosPopup => class ClosePosPopup extends _ClosePosPopup {
        /**
         * Extended to always allow the user to end the session (even if there are differences in the totals
         * payment and the money cashed).
         * 
         * The above only happens when the field `hide_totals_at_closing_session` is checked in the configurations
         * of this PoS.
         */
        canCloseSession () {
            return this.env.pos.config.hide_totals_at_closing_session || super.canCloseSession.call(this);
        }
        /**
         * Extended because the initial setUp of this component sets the `acceptClosing` state to False.
         * We need to set it to the value within the field `hide_totals_at_closing_session` in the configs.
         *
         * We also want to set all the input for entering the counted cash/money to zero.
         */
        async willStart() {
            const res = await super.willStart.call(this);
            if (this.state.acceptClosing = this.env.pos.config.hide_totals_at_closing_session)
                Object.values(this.state.payments).forEach(paymentInfo => paymentInfo.counted = 0);
            return res;
        }
        /**
         * Extended because the original method, sets the state acceptClosing to False after its execution.
         * We need to set it to the value within the field `hide_totals_at_closing_session` in the configs.
         */
        handleInputChange () {
            const res = super.handleInputChange.apply(this, arguments);
            this.state.acceptClosing = this.env.pos.config.hide_totals_at_closing_session;
            return res;
        }
        /**
         * Extended because the original method, sets the state acceptClosing to False after its execution.
         * We need to set it to the value within the field `hide_totals_at_closing_session` in the configs.
         */
        updateCountedCash () {
            const res = super.updateCountedCash.apply(this, arguments);
            this.state.acceptClosing = this.env.pos.config.hide_totals_at_closing_session;
            return res;
        }
    };
    
    Registries.Component.extend(ClosePosPopup, ClosePosPopupInherit);
});
