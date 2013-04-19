# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Vauxoo C.A. (http://openerp.com.ve/) All Rights Reserved.
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
from openerp.tools.translate import _



_transaction_form = '''<?xml version="1.0"?>
<form string="Last Cost Price Sum">
    <separator string="Sum By?" colspan="4"/>
    <field name="date_start" />
    <field name="date_end" />
    <newline/>
    <group col="4" colspan="2">
    <group col="4" colspan="2">
        <field name="u_check" />
        <field name="user_res_id" nolabel="1" attrs="{'readonly':[('u_check','!=',True)]}"/>
        <field name="u_sel" nolabel="1" attrs="{'readonly':[('u_check','!=',True)]}"/>
        <field name="p_check" />
        <field name="partner_res_id" nolabel="1" attrs="{'readonly':[('p_check','!=',True)]}"/>
        <field name="p_sel" nolabel="1" attrs="{'readonly':[('p_check','!=',True)]}"/>
        <field name="c_check" />
        <field name="cat_res_id" nolabel="1" attrs="{'readonly':[('c_check','!=',True)]}"/>
        <field name="c_sel" nolabel="1" attrs="{'readonly':[('c_check','!=',True)]}"/>
    </group>

    </group>
</form>'''

_transaction_fields = {
    'date_start': {'string': 'Start Date', 'type': 'date', 'required': True},
    'date_end': {'string': 'End Date', 'type': 'date', 'required': True},
    'user_res_id': {'string': 'Salesman', 'type': 'many2one', 'relation': 'res.users', 'required': False},
    'partner_res_id': {'string': 'Partner', 'type': 'many2one', 'relation': 'res.partner', 'required': False},
    'cat_res_id': {'string': 'Category', 'type': 'many2one', 'relation': 'product.category', 'required': False},
    'u_check': {'string': 'Check salesman?', 'type': 'boolean'},
    'p_check': {'string': 'Check partner?', 'type': 'boolean'},
    'c_check': {'string': 'Check category?', 'type': 'boolean'},
    'u_sel': {
        'string': "Sequence",
        'type': 'selection',
        'selection': [('one', '1'), ('two', '2'), ('three', '3'), ('none', 'No Filter')],
        'default': lambda *a: 'none'
    },
    'p_sel': {
        'string': "Sequence",
        'type': 'selection',
        'selection': [('one', '1'), ('two', '2'), ('three', '3'), ('none', 'No Filter')],
        'default': lambda *a: 'none'
    },
    'c_sel': {
        'string': "Sequence",
        'type': 'selection',
        'selection': [('one', '1'), ('two', '2'), ('three', '3'), ('none', 'No Filter')],
        'default': lambda *a: 'none'
    },


}


def _data_save(self, cr, uid, data, context):
    form = data['form']
    if not form['u_check'] and not form['p_check'] and not form['c_check']:
        raise wizard.except_wizard(_('User Error'), _(
            'You have to check one box !'))
    pool = pooler.get_pool(cr.dbname)
    prod_obj = pool.get('product.product')
    line_inv_obj = pool.get('account.invoice.line')
    updated_rep_line = []
    cond = ''
    valor = ''

# TODO

    if form['u_check']:
        vis = ('user', 'user_id', 'user_id', 'user_id')
        xml_id = 'action_profit_user_product_tree'
        if form['user_res_id']:
            valor = form['user_res_id']

    if form['p_check']:
        vis = ('partner', 'partner_id', 'partner_id', 'partner_id')
        xml_id = 'action_profit_partner_product_tree'
        if form['partner_res_id']:
            valor = form['partner_res_id']

    if form['c_check']:
        vis = ('category', 'cat_id', 'cat_id', 'cat_id')
        xml_id = 'action_profit_category_product_tree'
        if form['cat_res_id']:
            valor = form['cat_res_id']

    if form['u_check'] and form['p_check']:
        vis = ('uxp', '((user_id*1000000)+partner_id)',
               'user_id,partner_id', 'user_id,partner_id')
        xml_id = 'action_profit_uxp_product_tree'
        valor = ''
        if form['user_res_id']:
            cond = ' and user_id=%s' % form['user_res_id']
        if form['partner_res_id']:
            cond = ' and partner_id=%s' % form['partner_res_id']
        if form['user_res_id'] and form['partner_res_id']:
            cond = ' and user_id=%s and partner_id=%s' % (
                form['user_res_id'], form['partner_res_id'])

    if form['u_check'] and form['c_check']:
        vis = ('uxc', '((user_id*1000000)+cat_id)',
               'user_id,cat_id', 'user_id,cat_id')
        xml_id = 'action_profit_uxc_product_tree'
        valor = ''
        if form['user_res_id']:
            cond = ' and user_id=%s' % form['user_res_id']
        if form['cat_res_id']:
            cond = ' and cat_id=%s' % form['cat_res_id']
        if form['user_res_id'] and form['cat_res_id']:
            cond = ' and user_id=%s and cat_id=%s' % (
                form['user_res_id'], form['cat_res_id'])

    if form['p_check'] and form['c_check']:
        vis = ('pxc', '((cat_id*1000000)+partner_id)',
               'partner_id,cat_id', 'partner_id,cat_id')
        xml_id = 'action_profit_pxc_product_tree'
        valor = ''
        if form['partner_res_id']:
            cond = ' and partner_id=%s' % form['partner_res_id']
        if form['cat_res_id']:
            cond = ' and cat_id=%s' % form['cat_res_id']
        if form['partner_res_id'] and form['cat_res_id']:
            cond = ' and partner_id=%s and cat_id=%s' % (
                form['partner_res_id'], form['cat_res_id'])

    if form['u_check'] and form['p_check'] and form['c_check']:
        vis = ('upc', '((user_id*100000000000)+(cat_id*1000000)+partner_id)',
               'user_id,partner_id,cat_id', 'user_id,partner_id,cat_id')
        xml_id = 'action_profit_upc_product_tree'
        valor = ''
        if form['partner_res_id']:
            cond = ' and partner_id=%s' % form['partner_res_id']
        if form['cat_res_id']:
            cond = ' and cat_id=%s' % form['cat_res_id']
        if form['partner_res_id'] and form['cat_res_id']:
            cond = ' and partner_id=%s and cat_id=%s' % (
                form['partner_res_id'], form['cat_res_id'])
        if form['user_res_id'] and form['partner_res_id']:
            cond = ' and user_id=%s and partner_id=%s' % (
                form['user_res_id'], form['partner_res_id'])
        if form['user_res_id'] and form['cat_res_id']:
            cond = ' and user_id=%s and cat_id=%s' % (
                form['user_res_id'], form['cat_res_id'])
        if form['user_res_id'] and form['partner_res_id'] and form['cat_res_id']:
            cond = ' and user_id=%s and partner_id=%s and cat_id=%s' % (
                form['user_res_id'], form['partner_res_id'], form['cat_res_id'])

    cond = valor and ' and '+vis[1]+'=%s' % valor or cond
    sql = """
        create or replace view report_profit_%s as (
        select
            %s as id,
            %s,
            SUM(last_cost) as sum_last_cost,
            SUM(price_subtotal) as sum_price_subtotal,
            SUM(qty_consol) as sum_qty_consol,
            p_uom_c_id
        from report_profit p
        where p.name>='%s' and p.name<='%s'%s
        group by %s,p_uom_c_id
    )
""" % (vis[0], vis[1], vis[2], form['date_start'], form['date_end'], cond, vis[3])

    sql2 = """SELECT id FROM report_profit_%s""" % vis[0]

    cr.execute(sql)
    cr.execute(sql2)
    res = cr.fetchall()
    updated_rep_line = map(lambda x: x[0], res)

    if None in updated_rep_line:
        raise wizard.except_wizard(_('User Error'), _(
            'You have to check salesman or product !'))

    mod_obj = pool.get('ir.model.data')
    act_obj = pool.get('ir.actions.act_window')

    # we get the model
    result = mod_obj._get_id(cr, uid, 'report_profit', xml_id)
    id = mod_obj.read(cr, uid, result, ['res_id'])['res_id']
    # we read the act window
    result = act_obj.read(cr, uid, id)
    result['res_id'] = updated_rep_line

    return result


class wiz_last_cost_sum(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch': _transaction_form, 'fields': _transaction_fields, 'state': [('end', 'Cancel'), ('change', 'Update')]}
        },
        'change': {
            'actions': [],
            'result': {'type': 'action', 'action': _data_save, 'state': 'end'}
        }
    }
wiz_last_cost_sum('profit.update.costprice.sum')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
