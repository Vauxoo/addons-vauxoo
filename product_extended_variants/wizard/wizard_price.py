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
from openerp.tools import float_is_zero

import logging
import time

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
            INNER JOIN mrp_bom_line as mbl ON mbl.bom_id = mb.id
            WHERE mb.product_id IS NOT NULL;
                ''')
        result = cr.fetchall()
        parents = set([r[0] for r in result if r[0] is not None])
        children = set([r[1] for r in result if r[1] is not None])
        root = list(parents - children)
        return root

    def execute_cron(self, cr, uid, ids=None, context=None):
        ids = ids or []
        context = context or {}
        product_obj = self.pool.get('product.product')
        product_ids = self._get_products(cr, uid, ids, context=context)
        context['message'] = ''
        count = 0
        total = len(product_ids)
        _logger.info(
            'Cron Job will compute {length} products'.format(length=total))
        msglog = 'Computing cost for product: [{prod_id}]. {count}/{total}  \n'
        msglog2 = 'Updated correctly: [{prod_id}]  from {old} to {new} {count}/{total}  \n'  # noqa
        IDENTIFIER = str(time.time())
        WHEN = time.ctime()
        logfname = '/tmp/update_cost_err{identifier}.log'.format(identifier=IDENTIFIER)  # noqa
        logfull = '/tmp/update_cost_fine{identifier}.log'.format(identifier=IDENTIFIER)  # noqa
        products = product_obj.browse(cr, uid, product_ids, context=context)
        for product in products:
            count += 1
            try:
                # Due to this is a huge batch process it is better use a nw
                # curso to avoid blocking process.
                _logger.info(msglog.format(prod_id=product.id,
                                           total=total,
                                           count=count))
                new = 'Never Setted'
                if not product.cost_method == 'standard':
                    new = 'Ignored Because product is not set as Standard'
                else:
                    context.update({'active_model': 'product.product',
                                    'active_id': product.id})

                    price_id = self.create(cr, uid,
                                           {'real_time_accounting': True,
                                            'recursive': True},
                                           context=context)

                    old = product.standard_price
                    self.compute_from_bom(cr, uid, [price_id], context=context)
                    new = product.standard_price
                    msg_ok = msglog2.format(prod_id=product.id,
                                            total=total,
                                            old=old,
                                            new=new,
                                            count=count)
                    _logger.info(msg_ok)
                    if old > new:
                        # TODO: show qty_on_hand
                        msg_err = 'name: - {name} - There is onhand:- ID: [{prod}] - Old: - {old} - New: - {new}\n'  # noqa
                        msg_err_save = msg_err.format(prod=product.id,
                                                      name=product.name,
                                                      new=new,
                                                      old=old)
                        _logger.error(msg_err_save)
                        with open(logfname, 'a') as errored_log:
                            errored_log.write(msg_err_save)
                        context['message'] = msg_err_save
                    else:
                        with open(logfull, 'a') as errored_log:
                            errored_log.write(msg_ok)
                        context['message'] = msg_ok
            except Exception as msg:  # pylint: disable=W0703
                new = msg
                _logger.error(msg)
                context['message'] = msg
            _logger.warning(context.get('message'))
            product_obj.message_post(cr, uid, [product.id],
                                     subject='Updated at %s at %s' % (IDENTIFIER, WHEN),  # noqa
                                     body=context.get('message'))
        admin_partner = self.pool.get('res.users').browse(cr,
                                                          uid,
                                                          uid).partner_id.id
        self.pool.get('res.partner').message_post(cr, uid, admin_partner,
                                                  subject="Successfully updated at %s " % WHEN,  # noqa
                                                  body="File is on %s for errors and in %s for Ok Products." % (logfname, logfull))  # noqa
        # /!\ TODO: Write log for products that were ignored
        return True

    def __execute_cron(self, cr, uid, ids=None, context=None):  # noqa
        '''
         This method is incorrectly designed due to the write on the product as
         obsolete should be a core feature not a cron feature.

         I do not delete it because I need review afterwards such feature.

         Dear Future me I am really sorry
        '''
        ids = ids or []
        context = context or {}
        product_obj = self.pool.get('product.product')
        precision_obj = self.pool.get('decimal.precision').precision_get(
            cr, uid, 'Account')
        user = self.pool.get('res.users').browse(cr, uid, uid, context)
        std_bottom_threshold = user.company_id.std_price_neg_threshold
        product_ids = self._get_products(cr, uid, ids, context=context)
        message = 'Old price {old}, New price {new}'
        context['message'] = ''
        count = 0
        total = len(product_ids)
        _logger.info(
            'Cron Job will compute {length} products'.format(length=total))
        msglog = 'Computing cost for product: [{prod_id}]. {count}/{total}'
        for product in product_ids:
            prod_brw = product_obj.browse(cr, uid, product)
            count += 1
            _logger.info(
                msglog.format(prod_id=product, total=total, count=count))

            if product_obj.fetch_product_bom_states(
                    cr, uid, product, state='obsolete', context=context):
                _logger.warning(
                    'product [%s] has obsolete children', product)
                continue

            # /!\ NOTE: Is it enough to call the qty like that?
            if prod_brw.qty_available == 0:
                prod_brw.write({'state': 'obsolete'})
                continue
            context.update(
                {'active_model': 'product.product',
                 'active_id': product})
            std_preview = self._onchange_recursive(
                cr, uid, ids, recursive=True,
                context=context).get(product, 0.0)
            old = prod_brw.standard_price
            diff = std_preview - old

            # /!\ NOTE: Is it the right precision
            if float_is_zero(diff, precision_obj):
                # Do not update it is worthless
                continue

            if old and diff / old < std_bottom_threshold and \
                    prod_brw.qty_available > 0 and \
                    prod_brw.state != 'end':
                # Write product as obsolete
                # /!\ NOTE: Will not this cause more concurrence
                prod_brw.write({'state': 'end'})

            price_id = self.create(
                cr, uid, {'real_time_accounting': True, 'recursive': True},
                context=context)
            try:
                if not prod_brw.cost_method == 'standard':
                    new = 'Ignored Because product is not set as Standard'
                else:
                    self.compute_from_bom(cr, uid, [price_id], context=context)
                    new = prod_brw.standard_price
            except Exception as msg:  # pylint: disable=W0703
                new = msg

            context['message'] = message.format(old=old, new=new)
            self._post_message(cr, uid, ids, context=context)
        # /!\ TODO: Write log for products that were ignored
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
