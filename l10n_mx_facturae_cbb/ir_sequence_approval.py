# -*- encoding: utf-8 -*-
from osv import osv
from osv import fields

class ir_sequence_approval(osv.osv):
    _inherit = 'ir.sequence.approval'
    
    _columns = {
        'cbb_image': fields.binary(u'Imagen de Código de Barras Bidimensional'),
    }
ir_sequence_approval()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
