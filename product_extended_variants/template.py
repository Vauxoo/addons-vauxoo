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


from openerp import models,  _, fields


class product_category(models.Model):
    _inherit = 'product.category'

    property_difference_price_account_id = fields.\
        Many2one('account.account',
                 'Price Diference Account',
                 company_dependent=True,
                 help='Account used to create the '
                 'journal item changes in the '
                 'Standard Price')


class product_template(models.Model):
    _inherit = 'product.template'

    property_difference_price_account_id = fields.\
        Many2one('account.account',
                 'Price Diference Account',
                 company_dependent=True,
                 help='Account used to create the '
                 'journal item changes in the '
                 'Standard Price')

    def get_product_accounts(self, cr, uid, product_id, context=None):
        context = context or {}
        res = super(product_template, self)\
            .get_product_accounts(cr, uid, product_id,
                                  context=context)
        product_obj = self.pool.get('product.product')
        product_brw = product_obj.browse(cr, uid, product_id)
        diff_acc_id = product_brw.property_difference_price_account_id and  \
            product_brw.property_difference_price_account_id.id or False
        if not diff_acc_id:
            diff_acc_id = product_brw.categ_id.property_difference_price_account_id and  \
                product_brw.categ_id.property_difference_price_account_id.id or\
                False
        res.update({'property_difference_price_account_id': diff_acc_id})
        return res

    def compute_price(self, cr, uid, product_ids, template_ids=False,
                      recursive=False, test=False, real_time_accounting=False,
                      context=None):
        '''
        Will return test dict when the test = False
        Multiple ids at once?
        testdict is used to inform the user about the changes to be made
        '''
        testdict = {}
        real_time = real_time_accounting
        if product_ids:
            ids = product_ids
            model = 'product.product'
        else:
            ids = template_ids
            model = 'product.template'
        for prod_id in ids:
            bom_obj = self.pool.get('mrp.bom')
            if model == 'product.product':
                bom_id = bom_obj._bom_find(cr, uid,
                                           product_id=prod_id, context=context)
            else:
                bom_id = bom_obj._bom_find(cr, uid, product_tmpl_id=prod_id,
                                           context=context)
            if bom_id:
                # In recursive mode, it will first compute the prices of child
                # boms
                if recursive:
                    # Search the products that are components of this bom of
                    # prod_id
                    bom = bom_obj.browse(cr, uid, bom_id, context=context)

                    # Call compute_price on these subproducts
                    prod_set = set([x.product_id.id for x in bom.bom_line_ids])
                    res = self.\
                        compute_price(cr, uid, product_ids=list(prod_set),
                                      template_ids=[], recursive=recursive,
                                      test=test,
                                      real_time_accounting=real_time,
                                      context=context)
                    if test:
                        testdict.update(res)
                # Use calc price to calculate and put the price on the product
                # of the BoM if necessary
                price = self._calc_price(cr, uid,
                                         bom_obj.browse(cr, uid,
                                                        bom_id,
                                                        context=context),
                                         test=test,
                                         real_time_accounting=real_time,
                                         context=context)
                if test:
                    testdict.update({prod_id: price})
        if test:
            return testdict
        else:
            return True

    def do_change_standard_price(self, cr, uid, ids, new_price, context=None):
        """ Changes the Standard Price of Product and creates an account move
        accordingly."""
        location_obj = self.pool.get('stock.location')
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        if context is None:
            context = {}
        user_company_id = self.pool.get('res.users').browse(cr,
                                                            uid, uid,
                                                            context=context).\
            company_id.id
        loc_ids = location_obj.search(cr, uid,
                                      [('usage', '=', 'internal'),
                                       ('company_id', '=', user_company_id)])
        for rec_id in ids:
            datas = self.get_product_accounts(cr, uid, rec_id, context=context)
            for location in location_obj.browse(cr, uid, loc_ids,
                                                context=context):
                c = context.copy()
                c.update({'location': location.id, 'compute_child': False})
                product = self.browse(cr, uid, rec_id, context=c)

                diff = product.standard_price - new_price
                if not diff:
                    continue
                for prod_variant in product.product_variant_ids:
                    qty = prod_variant.qty_available
                    if qty:
                        # Accounting Entries
                        move_vals = {
                            'journal_id': datas['stock_journal'],
                            'company_id': location.company_id.id,
                        }
                        move_id = move_obj.create(cr, uid, move_vals,
                                                  context=context)

                        if diff*qty > 0:
                            amount_diff = qty * diff
                            debit_account_id = datas['stock_account_input']
                            credit_account_id = \
                                datas['property_stock_valuation_account_id']

                        else:
                            amount_diff = qty * -diff
                            debit_account_id = \
                                datas['property_stock_valuation_account_id']
                            credit_account_id = datas['stock_account_output']

                        move_line_obj.create(cr, uid, {
                            'name': _('Standard Price changed'),
                            'account_id': debit_account_id,
                            'debit': amount_diff,
                            'ref': '[{code}] {name}'.
                            format(code=prod_variant.default_code,
                                   name=prod_variant.name),
                            'credit': 0,
                            'move_id': move_id, }, context=context)
                        move_line_obj.create(cr, uid, {
                            'name': _('Standard Price changed'),
                            'account_id': credit_account_id,
                            'debit': 0,
                            'ref': '[{code}] {name}'.
                            format(code=prod_variant.default_code,
                                   name=prod_variant.name),
                            'credit': amount_diff,
                            'move_id': move_id
                            }, context=context)
            self.write(cr, uid, rec_id, {'standard_price': new_price})
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
