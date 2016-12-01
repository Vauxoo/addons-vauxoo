# coding: utf-8
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-Today OpenERP SA (<http://www.openerp.com>)
#
#    programmed by: Oscar Alcala: oscar@vauxoo.com
#    programmed by: Jose Morales: jose@vauxoo.com
#
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################


{
    "name": "AutoMerge Records",
    "version": "8.0.0.1.6",
    "author": "Vauxoo",
    "category": "Tools",
    "website": "http://www.serpentcs.com",
    "license": "AGPL-3",
    'depends': [
        'base'
    ],
    'data': [
        'security/merge_security.xml',
        'security/ir.model.access.csv',
        'merge_editing_view.xml',
    ],
    "installable": False,
    'application': True,
    'auto_install': False,
}
