# -*- encoding: utf-8 -*-
# Author=Nhomar Hernandez nhomar@vauxoo.com
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

{
    "name" : "Customs Information on lots",
    "version" : "0.1",
    "author" : "Vauxoo",
    "category" : "Localization/Mexico",
    "website": "http://www.vauxoo.com/",
    "description": """
Make relation between information of import with goverment.
With this module you will be able to make a relation between invoice and Information of importing transaction.
It will work as production lot make better control with quantities.
    """,
    "depends" : ["base","product","stock","account","procurement"],
    "demo" : [
    'demo/import_info_demo.xml',
    ],
    "update_xml" : [
        'security/ir.model.access.csv',
        'import_info_view.xml',
        'product_view.xml',
        'stock_view.xml',
        'label_report.xml',
        'security/groups.xml',
        'invoice_view.xml'
    ],
    "active": False,
    "installable": True
}
