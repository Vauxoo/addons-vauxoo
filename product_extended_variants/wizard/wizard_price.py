# -*- encoding: utf-8 -*-
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


class wizard_price(models.TransientModel):
    _inherit = "wizard.price"

    def default_get(self, cr, uid, field, context=None):
        res = super(wizard_price, self).default_get(cr,
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

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
