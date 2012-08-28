# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Luis Torres (luis_t@vauxoo.com)
############################################################################
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
from osv import osv
from osv import fields

class cer_config(osv.osv_memory):
    _name = 'cer.config'
    _inherit = 'res.config'
    
    def execute(self, cr, uid, ids, context=None):
        #~ company_obj=self.pool.get('res.company').browse(cr, uid, ids, context=context)
        #~ print 'company_obj',company_obj
        #~ user_obj=self.pool.get('res.users').browse(cr, uid, ids, context=context).company_id
        #~ id_company=company_obj.search(cr, uid, [('id', '=', user_obj)])
        #~ print 'id_company',id_company
        company_id=self.pool.get('res.users').browse(cr,uid,[uid],context)[0].company_id.partner_id.id
        list_company=[company_id]
        return {
                'name': 'Company',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'res.company.facturae.certificate',
                'type': 'ir.actions.act_window',
                'domain': [('id', 'in', list_company)],
                }
                
    _columns={
        'cif_file': fields.binary('CIF',help="Fiscal Identification Card"),
    }
        
    #~ def _action_add_production(self, cr, uid, ids, context=None):
        #~ id_company=self.pool.get('res.company')
        #~ 
        #~ print 'id_company',id_company
        #~ return {
                #~ 'name': 'Company',
                #~ 'view_type': 'form',
                #~ 'view_mode': 'tree,form',
                #~ 'res_model': 'res.company.facturae.certificate',
                #~ 'type': 'ir.actions.act_window',
                #~ 'domain': [('id', 'in', list_orders)],
                #~ }

cer_config()
