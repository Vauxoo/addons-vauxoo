# coding: utf-8
# © 2016 Vauxoo - http://www.vauxoo.com
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# info Vauxoo (info@vauxoo.com)
# coded by: karen@vauxoo.com
# planned by: nhomar@vauxoo.com

from datetime import datetime
from openerp import api, models
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


class CancelOrders(models.Model):
    """Inherit the sale.order model in order to cancel orders that have
    created more than 24 hours
    """

    _inherit = 'sale.order'

    @api.multi
    def cancel_old_orders(self):
        sale_order_obj = self.env['sale.order']
        rel_date = datetime.today() - relativedelta(days=1)
        strf_date = rel_date.strftime('%Y-%m-%d %H:%M:%S')
        draft_order = sale_order_obj.search([
            ('state', '=', 'draft'),
            ('partner_id', '=', self.env.ref('base.public_user').id),
            ('date_order', '<=', strf_date)
        ])
        _logger.info("Cancelling %s" % len(draft_order))
        for order in draft_order:
            order.action_cancel()
            _logger.info("Cancelling this order id: %s" % order.id)
