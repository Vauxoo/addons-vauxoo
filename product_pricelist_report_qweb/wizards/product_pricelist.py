from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ProductPriceList(models.TransientModel):
    _inherit = 'product.price_list'
    _description = 'Price List'
    _rec_name = 'price_list'

    report_format = fields.Selection([
        ('pdf', 'PDF'),
        # TODO: enable print on controller to HTML
        # ('html', 'HTML'),
        ('xls', 'Spreadsheet')], default='pdf')
    cost = fields.Boolean()
    margin_cost = fields.Boolean('Exp. Marg. Cost (%)')
    margin_sale = fields.Boolean('Exp. Marg. Sale (%)')
    only_prod_pricelist = fields.Boolean(
        'Only products in pricelist', help='If you active this field the products that are not in pricelist will '
        'have in the report the price in zero', default=True)
    products_with_price = fields.Boolean(
        'Only products with price', help='If this field is active, only will to add the products that have price.')

    @api.multi
    def print_report(self):
        """To get the date and print the report
        @return : return report
        """
        company = self.env.user.company_id
        if not company.logo:
            raise UserError(_("You have to set a logo or a layout for your company."))
        if not company.external_report_layout:
            raise UserError(_("You have to set your reports's header and footer layout."))

        datas = {'ids': self.env.context.get('active_ids', [])}
        field_list = [
            'price_list', 'qty1', 'qty2', 'qty3', 'qty4', 'qty5',
            'report_format', 'margin_cost', 'margin_sale',
            'only_prod_pricelist', 'products_with_price']
        res = self.read(field_list)
        res = {} if not res else res[0]
        res['price_list'] = res['price_list'][0]

        if res.get('margin_cost') or res.get('margin_sale'):
            res['qty1'] = 1.0
            for idx in range(2, 6):
                res['qty%d' % idx] = 0.0

        context = {
            'xls_report': res.get('report_format') == 'xls',
            'only_prod_pricelist': res.get('only_prod_pricelist', False),
            'products_with_price': res.get('products_with_price', False),
            'margin_cost': res['margin_cost'],
            'margin_sale': res['margin_sale'],
        }
        datas['form'] = res
        return self.env.ref('product.action_report_pricelist').with_context(context).report_action([], data=datas)
