from osv import osv
from osv import fields

class res_partner(osv.osv):
    _inherit = 'res.partner'
    _columns = {
        'description_invoice': fields.text("Description Invoice")
    }
res_partner()
