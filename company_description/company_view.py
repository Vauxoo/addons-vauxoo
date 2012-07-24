from osv import osv, fields

class res_company(osv.osv):
    _inherit = 'res.company'
    _columns = {
        'description_invoice': fields.text('Description Invoice',translate=True),
        'description_sale': fields.text('Description Sale',translate=True),
        'description_purchase': fields.text('Description Purchase',translate=True),
    }
res_company()
