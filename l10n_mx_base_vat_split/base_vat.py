# -*- coding: utf-8 -*-
from osv import osv, fields
from tools.translate import _

class res_partner(osv.osv):
    _inherit = 'res.partner'
    
    def _get_base_vat_split(self, cr, uid, ids, field_names=None, arg=False, context={}):
        if not context:
            context = {}
        res = {}
        for partner in self.browse(cr, uid, ids, context=context):
            res[partner.id] = partner.vat and partner.vat[2:] or False
        return res
    
    _columns = {
        'vat_split': fields.function(_get_base_vat_split, method=True, type='char', size=64, string='VAT Split', store=True),
    }
res_partner()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
