from osv import fields, osv

class res_users(osv.osv):
    _inherit = 'res.users'
    _columns = {
        'signature_logo': fields.binary('Signature Logo')
     }
res_users()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
