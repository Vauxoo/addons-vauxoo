# -*- encoding: utf-8 -*-
##############################################################################
# Copyright (c) 2011 Vauxoo (http://vauxoo.com)
# All Rights Reserved.
# Programmed by: Israel Fermín Montilla  <israel@vauxoo.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
###############################################################################
{
    "name": "M321 Customizations", 
    "version": "0.1", 
    "author": "Vauxoo", 
    "category": "Custom", 
    "description": """M321 needed models and views customizations1""", 
    "website": "http://vauxoo.com", 
    "license": "", 
    "depends": [
        "base", 
        "stock", 
        "product_icecat", 
        "account_cancel", 
        "sale", 
        "cost_structure"
    ], 
    "demo": [], 
    "data": [
        "security/pay_picking_security.xml", 
        "security/ir.model.access.csv", 
        "product_view.xml", 
        "invoice_view.xml", 
        "sale_view.xml", 
        "stock_view.xml", 
        "wizard/cancel_order_view.xml", 
        "wizard/supplier_asigner_view.xml", 
        "sale_workflow.xml"
    ], 
    "test": [], 
    "js": [], 
    "css": [], 
    "qweb": [], 
    "installable": True, 
    "auto_install": False
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: