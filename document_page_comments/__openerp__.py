# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
###############Credits######################################################
#    Coded by: Vauxoo C.A. (Yanina Aular & Miguel Delgado)
#    Planified by: Rafael Silva
#    Audited by: Vauxoo C.A.
##############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    "name": "Document Page Comments", 
    "version": "0.6", 
    "author": "Vauxoo", 
    "category": "Generic Modules", 
    "website": "http://vauxoo.com", 
    "license": "", 
    "depends": [
        "base", 
        "document_page", 
        "vauxoo_cms"
    ], 
    "demo": [], 
    "data": [
        "view/document_page_view.xml", 
        "data/document_pages_data.xml"
    ], 
    "test": [], 
    "js": [], 
    "css": [], 
    "qweb": [], 
    "installable": True, 
    "auto_install": False, 
    "active": False
}