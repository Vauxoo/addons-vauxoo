# coding: utf-8
#
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
#
{
    "name": "Expired Task Information",
    "version": "8.0.0.0.6",
    "author": "Vauxoo",
    "category": "Project",
    "website": "http://www.vauxoo.com",
    "license": "",
    "depends": [
        "base",
        "project"
    ],
    "demo": [],
    "data": [
        "security/config_task_security.xml",
        "security/ir.model.access.csv",
        "view/task_expiry_config_view.xml",
        "data/config_task_expired_data.xml"
    ],
    "test": [],
    "js": [],
    "css": [],
    "qweb": [],
    "installable": True,
    "auto_install": False,
}
