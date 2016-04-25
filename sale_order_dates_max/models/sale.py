# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Vauxoo Consultores (info@vauxoo.com)
############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime, timedelta


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    @api.multi
    @api.depends('order_line.product_id')
    def _get_commitment_date(self):
        """This method is overwrite because we need to get
            Commitment date field in base to max date of the
            sale order line
        """
        res = super(SaleOrder, self)._get_commitment_date(
            name='commitment_date', arg=None)
        dates_list = []
        for order in self:
            order.commitment_date = res.get(order.id, '')
            dates_list = []
            order_datetime = datetime.strptime(
                order.date_order, DEFAULT_SERVER_DATETIME_FORMAT)
            for line in order.order_line:
                if line.state == 'cancel':
                    continue
                dt_order = order_datetime + timedelta(days=line.delay or 0.0)
                dt_s = dt_order.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                dates_list.append(dt_s)
            if dates_list:
                # This is the change about the original method
                # changed min(dates_list)
                order.commitment_date = max(dates_list)

    commitment_date = fields.Datetime(
        compute='_get_commitment_date', store=True)
