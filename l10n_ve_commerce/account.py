# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import osv


class wizard_multi_charts_accounts(osv.TransientModel):

    """
    wizard_multi_charts_accounts(osv.osv_memory):
    """
    _inherit = 'wizard.multi.charts.accounts'

    def _get_chart(self, cr, uid, context=None):
        acc_tpl_obj = self.pool.get('account.chart.template')
        ids = acc_tpl_obj.search(
            cr, uid, [], order='create_date desc', context=context)
        if ids:
            return ids[0]
        return False

    def _get_default_accounts(self, cr, uid, context=None):
        accounts = []
        return accounts

    def _get_purchase_tax(self, cr, uid, context=None):
        ids = self.pool.get('account.chart.template').search(
            cr, uid, [], order='create_date desc', context=context)
        if ids:
            chart_template_id = ids[0]
            purchase_tax_ids = self.pool.get('account.tax.template').search(cr,
                        uid, [
                            ("chart_template_id", "=", chart_template_id),
                            ('type_tax_use', 'in', ('purchase', 'all'))],
                order="sequence")
            return purchase_tax_ids and purchase_tax_ids[0] or False
        return False

    def _get_sale_tax(self, cr, uid, context=None):
        ids = self.pool.get('account.chart.template').search(
            cr, uid, [], order='create_date desc', context=context)
        if ids:
            chart_template_id = ids[0]
            sale_tax_ids = self.pool.get('account.tax.template').search(cr,
                        uid, [("chart_template_id", "=", chart_template_id),
                              ('type_tax_use', 'in', ('sale', 'all'))],
                order="sequence")
            return sale_tax_ids and sale_tax_ids[0] or False
        return False

    _defaults = {
        'company_id': lambda self, cr, uid, c:
        self.pool.get('res.users').browse(cr, uid,
                                          [uid], c)[0].company_id.id,
        'chart_template_id': _get_chart,
        'bank_accounts_id': _get_default_accounts,
        'code_digits': 10,
        'sale_tax': _get_sale_tax,
        'purchase_tax': _get_purchase_tax,
        # 'seq_journal': True # no existe campo
    }
