##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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
{
    "name":"Product Catalog - Print Report of product catalog with product image",
    "version":"1.0",
    "author":"OpenERP S,A",
    "category":"Generic Modules/Inventory Control",
    "description": """
    This module use to print report of product catalog with product image, list price
    This module was ported to V6.0 by Vauxoo
    You need to save an image as attachment with the word "catalog" on its name,
    With this you will be able to see the image on report.
    The report will print all information related to product and prices related to 
    The partner selected to send the report.
    Go to Sales > Customers > Print Product Catalog to see the result.
    Try to save image with an square Npx X Npx resolution to avoid unspected redimension.
    """,
    "depends":["base","product"],
    "demo_xml":[],
    "update_xml":['product_report.xml','product_wizard.xml'],
    "active":False,
    "installable":True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

