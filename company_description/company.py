from osv import osv, fields

class res_company(osv.osv):
    _inherit = 'res.company'
    _columns = {
        'description_invoice': fields.text('Description Invoice'),
        'description_sale': fields.text('Description Sale'),
        'description_purchase': fields.text('Description Purchase'),
    }
res_company()
