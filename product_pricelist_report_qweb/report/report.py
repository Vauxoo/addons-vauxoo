#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
# #############Credits#########################################################
#    Coded by: Humberto Arocha <hbto@vauxoo.com>
###############################################################################
#    This program is free software: you can redistribute it and/or modify it
#    under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or (at your
#    option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################
import time

from openerp.osv import osv
from openerp.report import report_sxw


class parser(report_sxw.rml_parse):
    _name = 'product.pricelist.report.parser'

    def __init__(self, cr, uid, name, context=None):
        super(parser, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
        })
        self.context = context

    def set_context(self, objects, data, ids, report_type=None):
        # This is a way of capturing objects as depicted in
        # odoo/addons/account/report/account_balance.py
        new_ids = ids
        return super(parser, self).set_context(objects, data, new_ids,
                                               report_type=report_type)


class product_pricelist_report_qweb(osv.AbstractModel):

    # _name = `report.` + `report_name`
    # report_name="product_pricelist_report_qweb.comm_salespeople_template"
    _name = 'report.product_pricelist_report_qweb.comm_salespeople_template'

    # this inheritance will allow to render this particular report
    _inherit = 'report.abstract_report'
    _template = 'product_pricelist_report_qweb.comm_salespeople_template'
    _wrapped_report_class = parser

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
