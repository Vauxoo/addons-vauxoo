odoo.define('pos_blind_close.tour.ClosePosPopup', require => {
    const { ClosePosPopup } = require('pos_blind_close.helpers.ClosePosPopup');
    const { ProductScreen } = require('point_of_sale.tour.ProductScreenTourMethods');
    const { getSteps, startSteps } = require('point_of_sale.tour.utils');
    const Tour = require('web_tour.tour');

    startSteps();
    ProductScreen.do.confirmOpeningPopup();
    ClosePosPopup.do.ClosePosButton();
    ClosePosPopup.check.RemovedExpectedAndDifferenceHeaders();
    ClosePosPopup.check.RemovedExpectedAndDifferenceValues();

    Tour.register('pos_blind_close_ClosePosPopup', { test: true, url: '/pos/ui' }, getSteps());
});
