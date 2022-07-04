odoo.define('pos_blind_close.helpers.ClosePosPopup', require => {
    const { createTourMethods } = require('point_of_sale.tour.utils');

    class Do {
        ClosePosButton () {
            return [
                {
                    content: "close the Point of Sale frontend",
                    trigger: ".status-buttons .header-button",
                }
            ];
        }
    }

    class Check {
        RemovedExpectedAndDifferenceHeaders () {
            return [
                {
                    content: "Check the 'Expected' and 'Diference' header are gone",
                    trigger: ".modal-dialog .payment-methods-overview",
                    run () {
                        const $headers = $('.payment-methods-overview table thead tr');
                        if ($headers.find(':contains(Expected)').length) console.error('Expected header found!')
                        if ($headers.find(':contains(Difference)').length) console.error('Difference header found!')
                    }
                }
            ];
        }
        RemovedExpectedAndDifferenceValues () {
            return [
                {
                    content: "Check the 'Expected' and 'Diference' values are gone",
                    trigger: ".modal-dialog .payment-methods-overview",
                    run () {
                        // Each row of this line is gonna be a line of values.
                        // [0] Name of the payment method
                        // [1] Expected ammount
                        // [2] Input to enter amounts
                        // [3] The difference of inputed amounts
                        $('.payment-methods-overview table tbody tr').each(function () {
                            const $children = $(this).children();
                            if ($children.length > 2) 
                               console.error(`Unexpected value found in ${$children.eq(0)}`)
                        })
                    }
                }
            ];
        }
    }

    return createTourMethods('ClosePosPopup', Do, Check);
});
