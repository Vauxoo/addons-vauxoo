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

'''
Fiscal Report For Venezuela
'''

import time
from openerp.report import report_sxw


class trial_c(report_sxw.rml_parse):
    '''
    Book generates purchase and sale
    '''

    def __init__(self, cr, uid, name, context):
        '''
        Reference to the current instance
        '''
        super(trial_c, self).__init__(cr, uid, name, context)
        self.total = 0.0
        self.localcontext.update({
            'time': time,
            'get_partner_addr': self._get_partner_addr,
            'get_rif': self._get_rif,
            'get_data': self._get_data,
            'get_partner': self._get_partner,
            'get_category': self._get_category,
            'get_user': self._get_user,
        })

    def _get_partner_addr(self, idp=None):
        '''
        Obtains the address of partner
        '''
        if not idp:
            return []

        addr_obj = self.pool.get('res.partner.address')
        addr_inv = 'NO HAY DIRECCION FISCAL DEFINIDA'
        addr_ids = addr_obj.search(self.cr, self.uid, [(
            'partner_id', '=', idp), ('type', '=', 'invoice')])
        if addr_ids:
            addr = addr_obj.browse(self.cr, self.uid, addr_ids[0])
            addr_inv = (addr.street or '')+' '+(addr.street2 or '')+' '+(addr.zip or '') + ' '+(
                addr.city or '') + ' ' + (addr.country_id and addr.country_id.name or '') + ', TELF.:'+(addr.phone or '')
        return addr_inv

    def _get_rif(self, vat=''):
        '''
        Get R.I.F.
        '''
        if not vat:
            return []
        return vat[2:].replace(' ', '')

    def _get_data(self, form):
        pool = pooler.get_pool(self.cr.dbname)
        line_ids = []
        cond = ''
        valor = ''
        res = []

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
            vis = (
                'upc', '((user_id*100000000000)+(cat_id*1000000)+partner_id)',
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

        history = []
        for i in range(4):
            self.cr.execute("""select
                            %s as id,
                            %s,
                            SUM(last_cost) as sum_last_cost,
                            SUM(price_subtotal) as sum_price_subtotal,
                            SUM(qty_consol) as sum_qty_consol,
                            p_uom_c_id
                        from report_profit p
                        where p.name>='%s' and p.name<='%s'%s
                        group by %s,p_uom_c_id""" % (vis[1], vis[2], form[str(i)]['start'], form[str(i)]['stop'], cond, vis[3]))

            t = self.cr.fetchall()
            field_str = 'id,'+vis[2]+',slc,sps,sqc,uda'
            field_lst = field_str.split(',')
            d = {}
            for i in t:
                d[i[0]] = {}
                if i[0] not in line_ids:
                    line_ids.append(i[0])
                if len(i) != len(field_lst):
                    raise wizard.except_wizard(_(
                        'System Error'), _('Incorrect Field List!'))
                for j in range(len(i)):
                    d[i[0]].setdefault(field_lst[j], i[j])

            history.append(d)

        for l_id in line_ids:
            values = {}
            dtot = {
                'slc': 0.0,
                'sps': 0.0,
                'sqc': 0.0
            }
            for i in range(4):
                during = False
                if l_id in history[i]:
                    during = [history[i][l_id]]
                values[str(i)] = during and during[0] or ""
                dtot['slc'] += during and during[0]['slc'] or 0.0
                dtot['sps'] += during and during[0]['sps'] or 0.0
                dtot['sqc'] += during and during[0]['sqc'] or 0.0

            values['t'] = dtot
            res.append(values)

#        print 'res: ',res

        return res

    def _get_partner(self, lst_dct):
        partner_obj = self.pool.get('res.partner')
        res = ''
        for d in lst_dct:
            if type(lst_dct[d]) == type(dict()) and 'partner_id' in lst_dct[d] and lst_dct[d]['partner_id']:
                res = partner_obj.browse(
                    self.cr, self.uid, lst_dct[d]['partner_id']).name
                break
        return res

    def _get_category(self, lst_dct):
        category_obj = self.pool.get('product.category')
        res = ''
        for d in lst_dct:
            if type(lst_dct[d]) == type(dict()) and 'cat_id' in lst_dct[d] and lst_dct[d]['cat_id']:
                res = category_obj.browse(
                    self.cr, self.uid, lst_dct[d]['cat_id']).name
                break
        return res

    def _get_user(self, lst_dct):
        user_obj = self.pool.get('res.users')
        res = ''
        for d in lst_dct:
            if type(lst_dct[d]) == type(dict()) and 'user_id' in lst_dct[d] and lst_dct[d]['user_id']:
                res = user_obj.browse(
                    self.cr, self.uid, lst_dct[d]['user_id']).name
                break
        return res


report_sxw.report_sxw(
    'report.profit.trial.cost',
    'report.profit',
    'addons/report_profit/report/trial_cost.rml',
    parser=trial_c,
    header=False
)
