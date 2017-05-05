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


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.multi
    def _get_domain_dates(self):
        domain = super(ProductProduct, self)._get_domain_dates()
        context = dict(self._context)
        from_date_expected = context.get('from_date_expected', False)
        to_date_expected = context.get('to_date_expected', False)
        if from_date_expected:
            domain.append(('date_expected', '>=', from_date_expected))
        if to_date_expected:
            domain.append(('date_expected', '<=', to_date_expected))
        return domain
