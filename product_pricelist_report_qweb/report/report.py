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
from openerp.osv import osv
from openerp.addons.product.report import product_pricelist


class product_pricelist_report_qweb(osv.AbstractModel):

    # As we are inheriting a report that was previously a particular report we
    # have to keep it like that, i.e., we will keep _name the same than the
    # original

    # _name = `report.` + `report_name` (FQN)
    # report_name="product.report_pricelist"
    _name = 'report.product.report_pricelist'

    # this inheritance will allow to render this particular report
    _inherit = 'report.abstract_report'
    # new template will be used this because we want something more customized
    _template = 'product_pricelist_report_qweb.report_template'
    # old wrapper class from original report will be used
    _wrapped_report_class = product_pricelist.product_pricelist

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
