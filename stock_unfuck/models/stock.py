# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: Jose Morales <jose@vauxoo.com>
#    Planned by: Nhomar Hernandez <nhomar@vauxoo.com>
#    Audited by: Jose Morales <jose@vauxoo.com>
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
from openerp import models


class StockQuant(models.Model):

    _inherit = 'stock.quant'

    # pylint: disable=W0102
    def quants_get_preferred_domain(self, qty, move, ops=False,
                                    lot_id=False, domain=None,
                                    preferred_domain_list=[]):
        """The original function tries to find quants in the given location for
        the given domain.
        This method is inherited to return specific quants if these are sending
        by context, if not the quant returned are the found for the original
        method.
        """
        context = self.env.context
        res = context.get('force_quant', False) or \
            super(StockQuant, self).quants_get_preferred_domain(
                qty, move, ops=False, lot_id=False, domain=None,
                preferred_domain_list=[])
        return res
