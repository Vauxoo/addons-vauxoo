# coding: utf-8
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2014 OpenERP S.A. (<http://www.openerp.com>).
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
from openerp import models, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def fetch_product_bom_states(
            self, cr, uid, ids, vals=None, state=None, bom_id=None,
            context=None):
        vals = dict(vals or {})
        context = dict(context or {})
        ids = isinstance(ids, (int, long)) and ids or ids[0]

        def _bom_find(prod_id):
            bom_id = bom_obj._bom_find(
                cr, uid, product_id=prod_id, context=context)
            if bom_id:
                return bom_id
            prod_id = self.browse(
                cr, uid, prod_id, context=context).product_tmpl_id.id
            return bom_obj._bom_find(
                cr, uid, product_tmpl_id=prod_id, context=context)

        bom_obj = self.pool.get('mrp.bom')

        if ids not in vals:
            vals[ids] = self.browse(cr, uid, ids, context=context).state
        if state is not None and vals[ids] == state:
            return True

        bom_id = bom_id or _bom_find(ids)
        if not bom_id:
            return False
        bom = bom_obj.browse(cr, uid, bom_id, context=context)

        # Call compute_price on these subproducts
        prod_set = set([x.product_id.id for x in bom.bom_line_ids])
        res = False
        for prod_id in prod_set:
            if self.fetch_product_bom_states(
                    cr, uid, prod_id, vals=vals, state=state, context=context):
                res = True
                break
        return res


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def get_product_accounts(self, cr, uid, product_id, context=None):
        context = context or {}
        res = super(ProductTemplate, self).get_product_accounts(
            cr, uid, product_id, context=context)
        product = self.browse(cr, uid, product_id)
        diff_acc_id = product.property_account_creditor_price_difference and \
            product.property_account_creditor_price_difference.id or \
            product.categ_id.\
            property_account_creditor_price_difference_categ and \
            product.categ_id.\
            property_account_creditor_price_difference_categ.id or False

        res.update({'property_difference_price_account_id': diff_acc_id})
        return res

    def do_change_standard_price(self, cr, uid, ids, new_price, context=None):
        """ Changes the Standard Price of Product and creates an account move
        accordingly."""
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        if context is None:
            context = {}
        user_company_id = self.pool.get('res.users').browse(
            cr, uid, uid, context=context).company_id.id
        for rec_id in ids:
            datas = self.get_product_accounts(cr, uid, rec_id, context=context)
            diff = self.browse(
                cr, uid, rec_id, context=context).standard_price - new_price
            if not diff:
                continue
            cr.execute("""
                SELECT DISTINCT
                    sl.id
                FROM stock_quant sq
                INNER JOIN stock_location sl ON sl.id = sq.location_id
                INNER JOIN product_product pp ON pp.id = sq.product_id
                WHERE
                    pp.product_tmpl_id = %s
                    AND sl.usage = 'internal'
                    AND sl.company_id = %s
                ;""", (rec_id, user_company_id))
            loc_ids = [val[0] for val in cr.fetchall()]
            for location_id in loc_ids:
                contextc = context.copy()
                contextc.update({'location': location_id,
                                 'compute_child': False})
                product = self.browse(cr, uid, rec_id, context=contextc)

                for prod_variant in product.product_variant_ids:
                    qty = prod_variant.qty_available
                    if not qty:
                        continue
                    # Accounting Entries
                    ref = '[%(code)s] %(name)s' % dict(
                        code=prod_variant.default_code, name=prod_variant.name)
                    move_vals = {
                        'journal_id': datas['stock_journal'],
                        'company_id': user_company_id,
                        'ref': ref,
                    }
                    move_id = move_obj.create(
                        cr, uid, move_vals, context=context)
                    if diff * qty > 0:
                        amount_diff = qty * diff
                        debit_account_id = datas[
                            'property_difference_price_account_id']
                        credit_account_id = datas[
                            'property_stock_valuation_account_id']
                    else:
                        amount_diff = qty * -diff
                        debit_account_id = datas[
                            'property_stock_valuation_account_id']
                        credit_account_id = datas[
                            'property_difference_price_account_id']

                    move_line_obj.create(cr, uid, {
                        'name': _('Standard Price changed'),
                        'account_id': debit_account_id,
                        'debit': amount_diff,
                        'ref': ref,
                        'credit': 0,
                        'move_id': move_id,
                        'product_id': prod_variant.id,
                    }, context=context)
                    move_line_obj.create(cr, uid, {
                        'name': _('Standard Price changed'),
                        'account_id': credit_account_id,
                        'debit': 0,
                        'ref': ref,
                        'credit': amount_diff,
                        'move_id': move_id,
                        'product_id': prod_variant.id,
                    }, context=context)
            self.write(cr, uid, rec_id, {'standard_price': new_price})
        return True
