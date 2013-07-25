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
from openerp.osv import fields, osv
from lxml import etree
from openerp import SUPERUSER_ID

class account_voucher(osv.Model):
    _inherit = 'account.voucher'
    
    def fields_view_get_address(self, cr, uid, arch, context={}):
        user_obj = self.pool.get('res.users')
        fmt = user_obj.browse(cr, SUPERUSER_ID, uid, context).\
            company_id.country_id
        fmt = fmt and fmt.address_format
        layouts = {
            'new_div': """
                <div class="oe_subtotal_footer_separator">
                    <field name="conciled" modifiers="{&quot;invisible&quot;:\
                    true}"/>
                    <label for="amount"/>
                    <button type="object" icon="terp-stock_format-scientific" \
                        name="compute_tax" class="oe_link oe_edit_only" \
                        string="(Update)" attrs="{'invisible': \
                        [('state','!=','draft')]}"/>
                </div>
            """
            }
        for k,v in layouts.items():
            if fmt and (k in fmt):
                doc = etree.fromstring(arch)
                for node in doc.xpath(
                    "//div[@class='oe_subtotal_footer_separator']"):
                    tree = etree.fromstring(v)
                    node.getparent().replace(node, tree)
                arch = etree.tostring(doc)
                break
        return arch
    
    def fields_view_get(self, cr, uid, view_id=None, view_type=False,
        context=None, toolbar=False, submenu=False):
        res = super(account_voucher, self).fields_view_get(cr, uid,
            view_id=view_id, view_type=view_type, context=context,
            toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            res['arch'] = self.fields_view_get_address(cr, uid, res['arch'],
                context=context)
        return res
        
    def _check_conciled(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for voucher in self.browse(cr, uid, ids, context=context):
            reconcile = False
            for line in voucher.move_ids:
                if line.reconcile_id or line.reconcile_partial_id:
                    reconcile = True
            if reconcile == False:
                res[voucher.id] = False
            else:
                res[voucher.id] = True
        return res
        
    def _voucher_search(self, cr, uid, obj, name, args, context=None):
        if not len(args):
            return []
        company_user = self.pool.get('res.users').browse(cr, uid, uid,
            context=context).company_id.id
        company_id = self.pool.get('res.company').browse(cr, uid, company_user,
            context=context).id
        list_voucher = []
        for voucher in self.search(cr, uid, [('state','=','posted'), (
            'company_id', '=', company_id)]):
            reconcile = False
            for line in self.browse(cr, uid, voucher, context=context).move_ids:
                if line.reconcile_id.id or line.reconcile_partial_id.id:
                    reconcile = True
                    break
                else:
                    reconcile = False
            if reconcile == False:
                list_voucher.append(voucher)
        return [('id', 'in', [x for x in list_voucher])]
        
    _columns = {
        'conciled' : fields.function(_check_conciled, type='boolean',
            string='References', method=True, fnct_search=_voucher_search)
        }
