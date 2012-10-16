# -*- coding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
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
from osv import fields, osv

class mrp_production(osv.osv):
    _inherit= "mrp.production"
    
    def product_id_change(self, cr, uid, ids, product_id, context=None):
        bom_obj=self.pool.get('mrp.bom')
        res=super(mrp_production, self).product_id_change(cr, uid, ids,product_id,context=None)
        bom=bom_obj.browse(cr,uid,[res['value']['bom_id']],context=context)
        res['value']['analytic_acc_mp']=bom and bom[0].analytic_acc_mp.id or False
        res['value']['analytic_acc_pt']=bom and bom[0].analytic_acc_pt.id or False
        return res
        
    _columns={
        'analytic_acc_mp': fields.many2one('account.analytic.account','Analytic Account MP',),
        'analytic_acc_pt': fields.many2one('account.analytic.account','Analytic Account PT',)
    }

        
class mrp_bom(osv.osv):
    _inherit= "mrp.bom"
    

    
    _columns={
        'analytic_acc_mp': fields.many2one('account.analytic.account','Analytic Account MP',),
        'analytic_acc_pt': fields.many2one('account.analytic.account','Analytic Account PT',)
    }

    
class mrp_production_product_line(osv.osv):
    _inherit= "mrp.production.product.line"
    
    _columns={
        'analytic_acc': fields.many2one('account.analytic.account','Analytic Account',)
    }
