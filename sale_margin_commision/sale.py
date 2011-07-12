# -*- encoding: utf-8 -*-
from osv import osv
from osv import fields
from tools.translate import _

class sale_order_line(osv.osv):
    """
    sale_order_line
    """


    def _check_commision(self, cr, uid, ids, field_name, arg, context):
        result ={}
        #TODO : Business Process
        for i in ids:
            result[i]=10
        return result


    _inherit = 'sale.order'
    _columns = {
        'commision': fields.function(_check_commision, method=True, type='float', string='Commision Rate', store=True),
    }


sale_order_line()
