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
from openerp import api, fields, models


class ProcurementOrder(models.Model):
    _inherit = "procurement.order"

    @api.model
    def _get_orderpoint_date_planned(self, orderpoint, start_date):
        """ Approach extracted from Odoo 9.0, using new orderpoint fields:
            'lead_type' and 'lead_days'

        To considering:
            In Odoo 8.0 addons this date planned is computed just using the
            seller delay as dynamic factor, and not include delay by resupply
            rules. To optimize this date should be checked if the orderpoint
            would be satisfied by a buy order, manufacturing order or a
            resupply request, avoiding take the buy order as the only rule,
            which is how comes from Odoo.
        """
        date_planned = fields.Datetime.to_string(start_date)
        delta_days = relativedelta(days=(orderpoint.lead_days or 0.0))
        if orderpoint.lead_type == 'supplier':
            date_planned = super(ProcurementOrder, self).\
                _get_orderpoint_date_planned(orderpoint, start_date)
        date_planned = fields.Datetime.to_string(
            fields.Datetime.from_string(date_planned) + delta_days)
        return date_planned
