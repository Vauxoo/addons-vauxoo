# coding: utf-8
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: Jose Suniaga <josemiguel@vauxoo.com>
#    planned by: Gabriela Quilarte <gabriela@vauxoo.com>
############################################################################

from dateutil.relativedelta import relativedelta
from openerp import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    shipping_date = fields.Datetime(
        compute='_compute_shipping_date',
        string='shipping Date', store=True, compute_sudo=True,
        help="Date by which the products are sure to be delivered. In contrast"
        " to commitment date, not only is taken into account the product lead"
        " time, but also the resupply delay, the delivery lead time from"
        " supplier and the manufacturing delay")

    @api.depends('date_order', 'order_line.delay',
                 'order_line.product_id', 'order_line.product_uom_qty')
    def _compute_shipping_date(self):
        """Compute the shipping date.

        To analyze shipping date should be check the following dates:
          - date when product is available in a order warehouse
          - date when product will come from others warehouses
          - date when product will come from a purchase order
          - date when product will come from a manufacturing order
        """

        for order in self:
            dates_list = []
            for line in order.order_line.filtered(
                    lambda x: x.state != 'cancel'):
                days = line.delay or 0.0
                date_expected = line.compute_warehouse_date()
                resupply_date = line.compute_resupply_date()
                manufacturing_date = line.compute_manufacturing_date()
                purchase_date = line.compute_purchase_date()
                shipping_date = date_expected and [date_expected] or (
                    (resupply_date and [resupply_date] or []) +
                    (purchase_date and [purchase_date] or []) +
                    (manufacturing_date and [manufacturing_date] or []))
                # when not exists shipping date in at least one order line,
                # then the result for all order is False because we can't
                # ensure all order lines can be delivered. To avoid that case,
                # you should has at least one supplier registered by product,
                # in this way, we ensure that product shipping date can be
                # compute by a purchase
                if not shipping_date:
                    dates_list = []
                    break
                # save on dates_list the best option for this order line
                dates_list += [min(shipping_date) + relativedelta(days=days)]
            order.shipping_date = dates_list and \
                fields.Datetime.to_string(max(dates_list)) or False

    @api.multi
    def onchange_requested_date(self, requested_date, shipping_date):
        """Warn if the requested dates is sooner than the shipping date"""
        res = super(SaleOrder, self).onchange_requested_date(
            requested_date, shipping_date)
        if 'warning' in res:
            res['warning'].update({
                'message': _("The date requested by the customer is "
                             "sooner than the shipping date. You may be "
                             "unable to honor the customer's request.")
            })
        return res

    @api.model
    def _prepare_order_line_procurement(self, order, line, group_id=False):
        res = super(SaleOrder, self)._prepare_order_line_procurement(
            order, line, group_id)
        if order.shipping_date:
            res['date_planned'] = order.shipping_date
        return res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def compute_warehouse_date(self, request_product_qty=None, warehouse=None):
        """ Determine the most early date where a product is sure that could
        be delivered from a given warehouse. If the forecasted quantity is
        not enough to complete product qty requested, then is returned False.

        :param product_qty: product quantity requested
        :param warehouse: warehouse where the product will be delivered
        :return: date when product would be delivered
        :rtype: Datetime or False
        """

        date_expected = False
        for line in self.filtered("order_id.warehouse_id"):
            warehouse_id = warehouse and warehouse.id or \
                line.order_id.warehouse_id.id
            date_order = fields.Datetime.from_string(line.order_id.date_order)
            product_qty = request_product_qty or line.product_uom_qty
            product = line.product_id.with_context(warehouse=warehouse_id)
            if product_qty > product.virtual_available:
                return False
            days = virtual_available = 0
            while product_qty > virtual_available:
                date_expected = date_order + relativedelta(days=days)
                to_date_expected = fields.Datetime.to_string(date_expected)
                virtual_available = product.with_context(
                    to_date_expected=to_date_expected).virtual_available
                days += 1

        return date_expected

    @api.multi
    def compute_resupply_date(self, request_product_qty=None, warehouse=None):
        """ Date when product will come to a given warehouse from
        others warehouses

        :param product_qty: product quantity requested
        :param warehouse: warehouse where the product will be delivered
        :return: date when product is available on warehouse
        :rtype: Datetime or False
        """

        resupply_date = False
        dates_list = []
        work_time = self.env.user.company_id.logistic_calendar_id
        for line in self.filtered("order_id.warehouse_id"):
            product_qty = request_product_qty or line.product_uom_qty
            if product_qty > line.product_id.virtual_available:
                return False
            supplied_wh = warehouse or line.order_id.warehouse_id
            # delivery_lead = line.order_id.compute_delivery_lead()
            resupply_routes = self.env['stock.location.route'].search([
                ('supplied_wh_id', '=', supplied_wh.id)])
            routes_dates = []
            for route in resupply_routes:
                days = sum(route.pull_ids.mapped('delay'))
                supplier_wh = route.supplier_wh_id
                date_expected = line.compute_warehouse_date(
                    warehouse=supplier_wh)
                if date_expected:
                    date_expected = work_time and work_time.\
                        compute_working_days(line.delay or 0.0, date_expected)
                    # no matter working days when is in transit
                    routes_dates += [date_expected + relativedelta(days=days)]
            if routes_dates:
                dates_list.append(min(routes_dates))
        # extract the date when could complete all lines
        if dates_list:
            resupply_date = max(dates_list)
        return resupply_date

    @api.multi
    def compute_purchase_date(self):
        """ Date when product will come to a given warehouse from a purchase
        order

        :return: date when product is available on warehouse
        :rtype: Datetime or False
        """

        purchase_date = False
        dates_list = []
        for line in self.filtered("order_id.warehouse_id"):
            if not line.order_id.warehouse_id.buy_to_resupply:
                return False
            date_order = fields.Datetime.from_string(line.order_id.date_order)
            if line.product_id.seller_ids:
                days = line.product_id.seller_delay
                dates_list += [date_order + relativedelta(days=days)]
        # extract the date when could complete all lines
        if dates_list:
            purchase_date = max(dates_list)
        return purchase_date

    @api.multi
    def compute_manufacturing_date(self):
        """ Date when product will come to a given warehouse from a
        manufacturing order
        :return: date when product is available on warehouse
        :rtype: Datetime or False
        """

        manufacturing_date = False
        dates_list = []
        for line in self.filtered("order_id.warehouse_id"):
            if not line.order_id.warehouse_id.manufacture_to_resupply:
                return False
            date_order = fields.Datetime.from_string(line.order_id.date_order)
            bom_dates = []
            for bom in line.product_id.bom_ids:
                days = line.product_id.produce_delay or 0.0
                warehouse_id = line.order_id.warehouse_id.id
                all_lines_available = True
                for bom_line in bom.bom_line_ids:
                    product_qty = bom_line.product_qty * line.product_uom_qty
                    product = bom_line.product_id.with_context(
                        warehouse=warehouse_id)
                    if product_qty > product.virtual_available:
                        all_lines_available = False
                if all_lines_available:
                    bom_dates += [date_order + relativedelta(days=days)]
            if bom_dates:
                dates_list.append(min(bom_dates))
        # extract the date when could complete all lines
        if dates_list:
            manufacturing_date = max(dates_list)
        return manufacturing_date
