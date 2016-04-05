# coding: utf-8
from openerp import api, models


class ProductReport(models.AbstractModel):
    _name = 'report.website_variants_extra.pprintable'

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        product_mdl = self.env['product.product']
        product = product_mdl.browse(self._ids)
        cat = product.public_categ_ids
        breadcrumb = []
        while cat:
            breadcrumb.append(cat.name)
            cat = cat.parent_id
        breadcrumb.reverse()
        breadcrumb = ' > '.join(breadcrumb)
        website_data = product.website_description.replace("md", "xs")
        docargs = {
            'docs': product,
            'breadcrumb': breadcrumb,
            'website_data': website_data,
        }
        return report_obj.render('website_variants_extra.pprintable', docargs)
