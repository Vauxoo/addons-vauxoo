# -*- encoding: utf-8 -*-
##############################################################################
#
#   OpenERP, Open Source Management Solution
#   Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#   $Id$
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields


class purchase_config_settings(models.TransientModel):
    _inherit = 'purchase.config.settings'

    default_purchase_requisition = fields.Boolean(
        "Generate Procurement using Call for Bids",
        default_model='product.template', default=True,
        help='Allows you to generate requisitions in automatic,' +
        ' when procurement orders are created')


class stock_config_settings(models.TransientModel):
    _inherit = 'stock.config.settings'

    default_purchase_requisition = fields.Boolean(
        "Generate Procurement using Call for Bids",
        default_model='product.template', default=True,
        help='Allows you to generate requisitions in automatic,' +
        ' when procurement orders are created')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
