# coding: utf-8

from openerp import models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def compute_price(self, cr, uid, product_ids, template_ids=False,
                      recursive=False, test=False, real_time_accounting=False,
                      context=None):
        '''
        Will return test dict when the test = False
        Multiple ids at once? (NO THIS METHOD USES RECURSION)
        testdict is used to inform the user about the changes to be made
        '''
        bom_obj = self.pool.get('mrp.bom')
        testdict = {}
        real_time = real_time_accounting
        ids = template_ids
        model = 'product.template'
        if product_ids:
            ids = product_ids
            model = 'product.product'

        def _bom_find(prod_id):
            if model == 'product.product':
                return bom_obj._bom_find(
                    cr, uid, product_id=prod_id, context=context)
            return bom_obj._bom_find(
                cr, uid, product_tmpl_id=prod_id, context=context)

        for prod_id in ids:
            bom_id = _bom_find(prod_id)
            if bom_id:
                # In recursive mode, it will first compute the prices of child
                # boms
                if recursive:
                    # Search the products that are components of this bom of
                    # prod_id
                    bom = bom_obj.browse(cr, uid, bom_id, context=context)

                    # Call compute_price on these subproducts
                    prod_set = set([x.product_id.id for x in bom.bom_line_ids])
                    res = self. compute_price(
                        cr, uid, product_ids=list(prod_set), template_ids=[],
                        recursive=recursive, test=test,
                        real_time_accounting=real_time, context=context)
                    if test:
                        testdict.update(res)
                # Use calc price to calculate and put the price on the product
                # of the BoM if necessary
                price = self._calc_price(
                    cr, uid, bom_obj.browse(cr, uid, bom_id, context=context),
                    test=test, real_time_accounting=real_time, context=context)
                if test:
                    testdict.update({prod_id: price})
        if test:
            return testdict
        return True
