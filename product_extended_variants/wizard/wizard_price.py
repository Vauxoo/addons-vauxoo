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
from __future__ import division

import logging
import time
import math
from datetime import datetime
from openerp import models, api, _
from openerp.osv import fields
from openerp.tools.safe_eval import safe_eval
import dateutil.relativedelta

_logger = logging.getLogger(__name__)


class WizardPrice(models.Model):
    _inherit = "wizard.price"

    def _get_products(self, cr, uid, ids=None, context=None):
        """Return all products which represent top parent in bom
        [x]---+   [y]
         |    |    |
         |    |    |
        [a]  [b]  [c]
         |    |
         |    |
        [t]  [u]
        That is x and y
        """
        cr.execute('''
            SELECT
            DISTINCT mb.product_id AS pp1,
                     mbl.product_id AS pp2
            FROM mrp_bom AS mb
            INNER JOIN mrp_bom_line as mbl ON mbl.bom_id = mb.id
            WHERE mb.product_id IS NOT NULL AND mb.active = True;
                ''')
        result = cr.fetchall()
        parents = set([r[0] for r in result if r[0] is not None])
        children = set([r[1] for r in result if r[1] is not None])
        root = list(parents - children)
        return root

    def execute_cron_splited(self, cr, uid, ids=None, number=10, context=None):
        """TODO: Separate in some more readable methods.
        TODO: Better doc.
        ids: list: Wired IDS list to compute.
        number: int:split thread to be called.
        context: special context if needed.
        """
        batch = str(time.time())
        if number < 3 or not isinstance(number, int):
            _logger.info(
                'Cowardly refused run the cron at %s because I need at least '
                'devide by 1', batch)
            return False
        cron_obj = self.pool.get('ir.cron')
        # Create a template of cron in order to set only the new values
        # afterwards.
        cron_tmpl = {
            'user_id': uid,
            'active': False,
            'priority': 100,
            'numbercall': 1,
            'doall': False,
            'model': 'wizard.price',
            'function': 'execute_cron',
            'nextcall': fields.datetime.now(),
        }

        def chunks(list_p, numb):
            """Split the list in "number" parts"""
            numb = max(1, numb)
            return [list_p[i:i + numb] for i in range(0, len(list_p), numb)]

        product_ids = self._get_products(cr, uid, ids, context=context)
        if not product_ids:
            _logger.info(
                'Cowardly refused run the cron at %s because I do not have '
                'elements to compute', batch)
            return False

        crons = 1
        if number:
            crons = int(math.ceil(len(product_ids)/float(number)))
        chunked = chunks(product_ids, crons and crons or 1)
        cron_name = 'ID Update Cost %s' % batch
        # First step:
        # I create the cronjobs first.
        cron_job_ids = []
        for plist in chunked:
            new_cron = cron_tmpl.copy()
            new_cron.update({
                'name': cron_name,
                'nextcall': fields.datetime.now(),
                'args': '[%(elements)s]' % dict(elements=str(plist)),
            })
            created = cron_obj.create(cr, uid, new_cron)
            cron_job_ids.append(created)
            _logger.info('Created cron job id [%s]', created)
        # Second Step:
        # I set postmortem the order because only here we now who is next and
        # who is before in terms of ID in database to pass is as parameter.
        cron_job_ids = sorted(cron_job_ids)
        for cron_id in cron_job_ids:
            cron = cron_obj.browse(cr, uid, cron_id)
            previous_cron = False
            next_cron = False
            if len(cron_job_ids) == 1:
                cron.write({'active': True})
            elif cron_id == min(cron_job_ids):
                cron.write({'active': True})
                next_cron = cron_job_ids[1]
            elif cron_id == max(cron_job_ids):
                previous_cron = cron_job_ids[-2]
            else:
                previous_cron = cron_job_ids[cron_job_ids.index(cron_id) - 1]
                next_cron = cron_job_ids[cron_job_ids.index(cron_id) + 1]
            new_args = safe_eval(cron.args)
            new_args.append(previous_cron)
            new_args.append(next_cron)
            variables = {
                'name': cron_name.replace('ID', str(cron_id)),
                'args': '(%s)' % str(new_args),
            }
            cron.write(variables)
            _logger.info('Setted the elements correct [%s]', cron_id)

        # self._create_update_crons
        return True

    def execute_cron(self, cr, uid, product_ids=None,
                     previous_cron=None, next_cron=None):
        context = {}
        total = len(product_ids)
        product_obj = self.pool.get('product.product')
        context['message'] = ''
        count = 0
        _logger.info(
            'Cron Job will compute %(length)s products', {'length': total})
        msglog = 'Computing cost for product: '\
            '[%(prod_id)s}]. %(count)s/%(total)s  \n'
        msglog2 = 'Updated correctly: [%(prod_id)s]  from %(old)s to %(new)s %(count)s/%(total)s  \n'  # noqa
        identifier_time = str(time.time())
        when_time = time.ctime()
        logfname = '/tmp/update_cost_err%(identifier)s.log' % dict(
            identifier=identifier_time)
        logfull = '/tmp/update_cost_fine%(identifier)s.log' % dict(
            identifier=identifier_time)
        products = product_obj.browse(cr, uid, product_ids, context=context)
        for product in products:
            count += 1
            try:
                # Due to this is a huge batch process it is better use a nw
                # curso to avoid blocking process.
                _logger.info(msglog, {
                    'prod_id': product.id,
                    'total': total,
                    'count': count})
                if product_obj.fetch_product_bom_states(
                        cr, uid, product.id, state='obsolete',
                        context=context):
                    _logger.warning(
                        'product [%s] has obsolete children', product)
                    continue
                context['message'] = 'Never Setted'
                if not product.cost_method == 'standard':
                    context['message'] = _(
                        'Ignored because product is not set as Standard')
                    continue
                context.update({'active_model': 'product.product',
                                'active_id': product.id})

                price_id = self.create(cr, uid, {
                    'real_time_accounting': True,
                    'recursive': True}, context=context)

                old = product.standard_price
                self.compute_from_bom(cr, uid, [price_id], context=context)
                new = product.standard_price
                msg_ok = msglog2 % {
                    'prod_id': product.id,
                    'total': total,
                    'old': old,
                    'new': new,
                    'count': count}
                _logger.info(msg_ok)
                if old > new:
                    # TODO: show qty_on_hand
                    msg_err = 'name: - {name} - There is onhand:- ID: [{prod}] - Old: - {old} - New: - {new}\n'  # noqa
                    msg_err_save = msg_err % dict(
                        prod=product.id, name=product.name, new=new, old=old)
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
            product_obj.message_post(
                cr, uid, [product.id], subject='Updated at %s at %s' % (
                    identifier_time, when_time),  body=context.get('message'))
        admin_partner = self.pool.get('res.users').browse(
            cr, uid, uid).partner_id.id
        self.pool.get('res.partner').message_post(
            cr, uid, admin_partner,
            subject="Successfully updated at %s " % when_time,
            body="File is on %s for errors and in %s for Ok Products." % (logfname, logfull))  # noqa
        if previous_cron:
            # TODO: It should be deleted but for now it is Ok!
            self.pool.get('ir.cron').write(cr, uid,
                                           [previous_cron], {'active': False})
        if next_cron:
            nextcall = (
                datetime.now() + dateutil.relativedelta.relativedelta(
                    minutes=1)).strftime('%Y-%m-%d %H:%M:%S')
            self.pool.get('ir.cron').write(
                cr, uid, [next_cron], {'active': True, 'nextcall': nextcall})
        # /!\ TODO: Write log for products that were ignored
        return True

    def default_get(self, cr, uid, field, context=None):
        res = super(WizardPrice, self).default_get(
            cr, uid, field, context=context)
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
            res['info_field'] = str(tmpl_obj.compute_price(
                cr, uid, [], template_ids=[product_obj.id], test=True,
                context=context))
        else:
            res['info_field'] = str(tmpl_obj.compute_price(
                cr, uid, product_ids=[product_obj.id], template_ids=[],
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
        product_ar = {}
        if res[0].recursive:
            product_ar = self.save_product_price(cr, uid, [prod.id], model)
        if model == 'product.template':
            tmpl_obj.compute_price(
                cr, uid, [], template_ids=[prod.id],
                real_time_accounting=res[0].real_time_accounting,
                recursive=res[0].recursive, test=False, context=context)
        else:
            tmpl_obj.compute_price(
                cr, uid, product_ids=[prod.id], template_ids=[],
                real_time_accounting=res[0].real_time_accounting,
                recursive=res[0].recursive, test=False, context=context)
        for prod in product_ar:
            self.pool.get('product.product').write(cr, uid, [prod], {
                'standard_price': product_ar.get(prod)
            })
        return True

    @api.model
    def save_product_price(self, prod_ids, model):
        """Save the standard price before to be updated to products with cost
        method different to 'standard_price'"""
        product_ar = self._context.get('product_ar', {})
        bom_obj = self.env['mrp.bom']
        for prod_id in prod_ids:
            if model == 'product.product':
                bom_id = bom_obj._bom_find(product_id=prod_id)
            else:
                bom_id = bom_obj._bom_find(product_tmpl_id=prod_id)
            if not bom_id:
                continue
            # Search the products that are components of this bom of prod_id
            bom = bom_obj.browse(bom_id)
            # Call compute_price on these subproducts
            prod_set = bom.bom_line_ids.mapped('product_id')
            prods = prod_set.filtered(lambda r: r.cost_method != 'standard')
            for prod in prods:
                if not product_ar.get(prod.id, False):
                    product_ar.update({prod.id: prod.standard_price})
            self.with_context(product_ar=product_ar).save_product_price(
                prod_set.ids, 'product.product')
        return product_ar
