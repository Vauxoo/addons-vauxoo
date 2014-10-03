# -*- encoding: utf-8 -*-
##############################################################################
# Copyright (c) 2011 Vauxoo (http://vauxoo.com)
# All Rights Reserved.
# Programmed by: Israel Fermin Montilla  <israel@vauxoo.com>
#                Nhomar Hernandez <nhomar@vauxoo.com>
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
    "name": "Deliver Project Report", 
    "version": "", 
    "author": "Vauxoo", 
    "category": "Generic Modules/Projects & Services", 
    "description": """
    Used to improve documentation module to deliver a report to customer one time
    project is delivered.

    TODO:
    List of modules Installed.
    List of menues (Adding help from action)
    List of Views (Adding printScreens)
    List of Tasks related (From Launchpad, Internal OpenERP, External OpenERP, CRM, Mails etc.)
    Funcional Intro
    Blueprints Related
    Hours
    Sales Orders related (From your own OpenERP Instance)
    Invoices Related (From your OpenERP Instance)
    """, 
    "website": "http://vauxoo.com", 
    "license": "", 
    "depends": [
        "base"
    ], 
    "demo": [], 
    "data": [
        "view/module_view.xml", 
        "report/ir_report.xml", 
        "report/module_report.xml"
    ], 
    "test": [], 
    "js": [], 
    "css": [], 
    "qweb": [], 
    "installable": True, 
    "auto_install": False, 
    "active": False
}