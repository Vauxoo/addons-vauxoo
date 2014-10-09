# -*- encoding: utf-8 -*-
############################################################################
#    Module Writen to OpenERP, Open Source Management Solution 
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved 
############## Credits######################################################
#    Coded by: Luis Escobar <luis@vauxoo.com>
#    Planified by: Nhomar Hernandez <nhomar@vauxoo.com>
#    Audited by: Humberto Arocha <humberto@vauxoo.com> 
############################################################################
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
############################################################################

from openerp.osv import fields, osv



class res_company(osv.Model):
    """
    res_company
    """

    _inherit = 'res.company'
    _columns = {
        'sale_report_id': fields.many2one('ir.actions.report.xml', 'Sale Order Report', required=False, domain="[('model','=','sale.order')]"),
    }
