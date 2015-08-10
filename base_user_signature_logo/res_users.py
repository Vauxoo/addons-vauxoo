from openerp.osv import osv, fields


class ResUsers(osv.Model):
    _inherit = 'res.users'
    _columns = {
        'signature_logo': fields.binary('Signature Logo')
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
