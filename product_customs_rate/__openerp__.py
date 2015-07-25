# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Cubic ERP - Teradata SAC (<http://cubicerp.com>).
#       (Modified by)   Vauxoo - http://www.vauxoo.com/
#                       info Vauxoo (info@vauxoo.com)
#    Modified by - juan@vauxoo.com
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
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
{
    "name": "Customs Rate Management", 
    "version": "1.5", 
    "author": "Cubic ERP & Vauxoo", 
    "category": "Finance", 
    "website": "http://cubicERP.com & http://vauxoo.com", 
    "license": "", 
    "depends": [
        "product", 
        "account"
    ], 
    "demo": [], 
    "data": [
        "security/product_customs_rate_security.xml", 
        "security/ir.model.access.csv", 
        "product_view.xml"
    ], 
    "test": [], 
    "js": [], 
    "css": [], 
    "qweb": [], 
    "installable": True, 
    "auto_install": False, 
    "active": False
}