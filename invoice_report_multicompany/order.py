# -*- encoding: utf-8 -*-
from osv import osv
from osv import fields
from tools.translate import _


class sale_order_line(osv.osv):
    """
    OpenERP Model : sale_order_line
    """
    _inherit = 'sale.order.line'
    _columns = {
        'att_bro': fields.boolean('Attach Brochure', required=False, help="If you ccheck this option, the first attachment related to the product_id marked as brochure will be printed as extra info with sale order"),
    }
sale_order_line()


class sale_order(osv.osv):
    """
    OpenERP Model : sale_order_line
    """
    _inherit = 'sale.order'

    def print_with_attachment(self, cr, user, ids, context={}):
        for o in self.browse(cr, user, ids, context):
            for ol in o.order_line:
                if ol.att_bro:
                    print "Im Here i will go to print %s " % ol.name
        return True
sale_order()
