# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Vauxoo C.A. (http://openerp.com.ve/) All Rights Reserved.
#                    Javier Duran <javier@vauxoo.com>
# 
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
#
##############################################################################

import wizard
import osv
import pooler
from tools.translate import _

_transaction_form = '''<?xml version="1.0"?>
<form string="Update Last Cost Price">
    <separator string="Analyze Unit of Last Cost Price" colspan="4"/>
     <field name="uom_c_id" widget="selection"/>
</form>'''

_transaction_fields = {    
    'uom_c_id': {'string':'Consolidate Unit', 'type':'many2one', 'relation': 'product.uom.consol','required':True},
   
}

def _data_save(self, cr, uid, data, context):
    pool = pooler.get_pool(cr.dbname)
    prod_obj = pool.get('product.product')
    line_inv_obj = pool.get('account.invoice.line')
    updated_inv_line = []

    cr.execute("""
        create or replace view report_profit as (
            select
                l.id as id,
                to_char(i.date_invoice, 'YYYY-MM-DD') as name,
                l.product_id as product_id,
                p.id as partner_id,
                u.id as user_id,
                l.quantity as quantity,
                case when i.type='out_refund'
                    then
                        l.price_unit*(-1)
                    else
                        l.price_unit 
                end as price_unit,
                case when i.type='out_refund'
                    then
                        l.last_price*(-1)
                    else
                        l.last_price 
                end as last_cost,                 
                case when i.type='out_refund'
                    then
                        l.price_subtotal*(-1)
                    else
                        l.price_subtotal 
                end as price_subtotal,
                case when i.type='out_refund'
                    then
                        (l.quantity*l.last_price)*(-1)
                    else
                        (l.quantity*l.last_price) 
                end as last_cost_subtotal,
                case when i.type='out_refund'
                    then
                        (price_subtotal-l.quantity*l.last_price)*(-1)
                    else
                        (price_subtotal-l.quantity*l.last_price)
                end as profit,
                case when i.type='out_refund'
                    then
                        ((price_subtotal-l.quantity*l.last_price)*(-1)/(price_subtotal)*100)
                    else
                        ((price_subtotal-l.quantity*l.last_price)/(price_subtotal)*100)
                end as perc,
                l.uos_id as uom_id,
                p.name as partner,
                i.type as type,
                c.p_uom_c_id as p_uom_c_id,
                case when i.type='out_refund'     
                    then                           
                        (l.quantity*c.factor_consol)*(-1)
                    else
                        (l.quantity*c.factor_consol)
                end as qty_consol,
                t.categ_id as cat_id
            from account_invoice i
                inner join res_partner p on (p.id=i.partner_id)
                left join res_users u on (u.id=p.user_id)
                right join account_invoice_line l on (i.id=l.invoice_id)
                left join product_uom m on (m.id=l.uos_id)
                left join product_uom_consol_line c on (m.id=c.p_uom_id)
                left join product_template t on (t.id=l.product_id)
                left join product_product d on (d.product_tmpl_id=l.product_id)
            where l.quantity != 0 and i.type in ('out_invoice', 'out_refund') and i.state in ('open', 'paid') and l.uos_id in (
                select
                    u.id as id
                from product_uom u
                    inner join product_uom_consol_line c on (u.id=c.p_uom_id)
                where c.p_uom_c_id=%s
            )
            group by l.id,to_char(i.date_invoice, 'YYYY-MM-DD'),l.product_id,p.id,u.id,l.quantity,l.price_unit,l.last_price,l.price_subtotal,l.uos_id,p.name,i.type,c.p_uom_c_id,c.factor_consol,t.categ_id

        )
    """, (data['form']['uom_c_id'],))
    sql = """
        SELECT id FROM report_profit"""
    cr.execute(sql)
    res = cr.fetchall()
    for line in line_inv_obj.browse(cr, uid, map(lambda x:x[0],res)):
        if line.invoice_id.state in ('open', 'paid'):
            inv_id = line.invoice_id.parent_id and line.invoice_id.parent_id.id or line.invoice_id.id            
            prod_price = prod_obj._product_get_price(cr, uid, [line.product_id.id], inv_id, False, line.invoice_id.date_invoice, context, ('open', 'paid'), 'in_invoice')
            if (not prod_price[line.product_id.id]) and line.product_id.seller_ids:
                supinfo_ids = []
                for sup in line.product_id.seller_ids:
                    supinfo_ids.append(sup.id)
                cr.execute('select max(price) from pricelist_partnerinfo where suppinfo_id in ('+','.join(map(str,supinfo_ids))+')')
                record = cr.fetchone()
                prod_price[line.product_id.id] = record and record[0] or False

            line_inv_obj.write(cr, uid,line.id, {'last_price':prod_price[line.product_id.id]}, context=context)
            updated_inv_line.append(line.id)
    #we get the view id
    mod_obj = pool.get('ir.model.data')
    act_obj = pool.get('ir.actions.act_window')

    xml_id = 'action_profit_product_tree'

    #we get the model
    result = mod_obj._get_id(cr, uid, 'report_profit', xml_id)
    id = mod_obj.read(cr, uid, result, ['res_id'])['res_id']
    # we read the act window
    result = act_obj.read(cr, uid, id)
    result['res_id'] = updated_inv_line


    return result

class wiz_last_cost2(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':_transaction_form, 'fields':_transaction_fields, 'state':[('end','Cancel'),('change','Update')]}
        },
        'change': {
            'actions': [],
            'result': {'type': 'action', 'action':_data_save, 'state':'end'}
        }
    }
wiz_last_cost2('profit.update.costprice2')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

