# coding: utf-8
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2011 OpenERP S.A. (<http://www.openerp.com>).
#    $Id$
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

from openerp import models,  _
import logging

_logger = logging.getLogger(__name__)


class WizardPrice(models.Model):
    _inherit = "wizard.price"

    def _post_message(self, cr, uid, ids=None, context=None):
        product_obj = self.pool.get('product.product')
        return product_obj.message_post(
            cr, uid, context.get('active_id'), body=context.get('message'),
            subject='Automatically Computed Standard Price')

    def _get_products(self, cr, uid, ids=None, context=None):
        '''
        Return all products which represent top parent in bom
        [x]---+   [y]
         |    |    |
         |    |    |
        [a]  [b]  [c]
         |    |
         |    |
        [t]  [u]
        That is x and y
        '''
        cr.execute('''
            SELECT
                DISTINCT mb.product_id AS pp1,
                mbl.product_id AS pp2
            FROM mrp_bom AS mb
            INNER JOIN mrp_bom_line as mbl ON mbl.bom_id = mb.id;
                ''')
        result = cr.fetchall()
        parents = set([r[0] for r in result])
        children = set([r[1] for r in result])
        root = list(parents - children)
        return root

    def execute_cron(self, cr, uid, ids=None, context=None):
        ids = ids or []
        context = context or {}
        product_obj = self.pool.get('product.product')
        product_ids = self._get_products(cr, uid, ids, context=context)
        message = 'Old price {old}, New price {new}'
        context['message'] = ''
        count = 0
        total = len(product_ids)
        _logger.info(
            'Cron Job will compute {length} products'.format(length=total))
        msglog = 'Computing cost for product: [{prod_id}]. {count}/{total}'
        for product in product_ids:
            count += 1
            _logger.info(
                msglog.format(prod_id=product, total=total, count=count))
            context.update({'active_model': 'product.product',
                            'active_id': product})
            price_id = self.create(cr, uid,
                                   {'real_time_accounting': True,
                                    'recursive': True},
                                   context=context)
            old = product_obj.browse(cr, uid, product).standard_price
            try:
                self.compute_from_bom(cr, uid, [price_id], context=context)
                new = product_obj.browse(cr, uid, product).standard_price
            except Exception as msg:  # pylint: disable=W0703
                new = msg

            context['message'] = message.format(old=old, new=new)
            self._post_message(cr, uid, ids, context=context)
        return True

    def default_get(self, cr, uid, field, context=None):
        res = super(WizardPrice, self).default_get(cr,
                                                   uid,
                                                   field, context=context)
        product_pool = self.pool.get(context.get('active_model',
                                                 'product.template'))
        tmpl_obj = self.pool.get('product.template')
        product_obj = product_pool.browse(cr, uid,
                                          context.get('active_id', False))
        if context is None:
            context = {}
        rec_id = context and context.get('active_id', False)
        assert rec_id, _('Active ID is not set in Context.')
        if context.get('active_model') == 'product.template':
            res['info_field'] = \
                str(tmpl_obj.
                    compute_price(cr, uid, [],
                                  template_ids=[product_obj.id],
                                  test=True, context=context))
        else:
            res['info_field'] = \
                str(tmpl_obj.
                    compute_price(cr, uid,
                                  product_ids=[product_obj.id],
                                  template_ids=[],
                                  test=True, context=context))
        return res

    def compute_from_bom(self, cr, uid, ids, context=None):
        assert len(ids) == 1
        if context is None:
            context = {}
        model = context.get('active_model')
        rec_id = context and context.get('active_id', False)
        assert rec_id, _('Active ID is not set in Context.')
        prod_obj = self.pool.get(model)
        tmpl_obj = self.pool.get('product.template')
        res = self.browse(cr, uid, ids, context=context)
        prod = prod_obj.browse(cr, uid, rec_id, context=context)
        if model == 'product.template':
            tmpl_obj.\
                compute_price(cr, uid, [],
                              template_ids=[prod.id],
                              real_time_accounting=res[0].real_time_accounting,
                              recursive=res[0].recursive,
                              test=False, context=context)
        else:
            tmpl_obj.\
                compute_price(cr, uid,
                              product_ids=[prod.id],
                              template_ids=[],
                              real_time_accounting=res[0].real_time_accounting,
                              recursive=res[0].recursive,
                              test=False, context=context)
        return True
