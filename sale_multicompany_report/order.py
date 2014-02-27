# -*- encoding: utf-8 -*-
from openerp.osv import fields, osv
from openerp.tools.translate import _



class sale_order_line(osv.Model):
    """
    OpenERP Model : sale_order_line
    """
    _inherit = 'sale.order.line'
    _columns = {
        'att_bro': fields.boolean('Attach Brochure', required=False, help="""If you check this
        option, the first attachment related to the product_id marked as brochure will be printed
        as extra info with sale order"""),
    }

class sale_order(osv.Model):
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

    def __get_company_object(self, cr, uid):
        user = self.pool.get('res.users').browse(cr, uid, uid)
        print user
        if not user.company_id:
            raise except_osv(_('ERROR !'), _(
                'There is no company configured for this user'))
        return user.company_id

    def _get_report_name(self, cr, uid, context):
        report = self.__get_company_object(cr, uid).sale_report_id
        if not report:
            rep_id = self.pool.get("ir.actions.report.xml").search(
                cr, uid, [('model', '=', 'sale.order'), ], order="id")[0]
            report = self.pool.get(
                "ir.actions.report.xml").browse(cr, uid, rep_id)
        return report.report_name

    def print_quotation(self, cr, uid, ids, context=None):
        pq = super(sale_order, self).print_quotation(cr,uid,ids, context)
        return  {'type': 'ir.actions.report.xml', 'report_name': self._get_report_name(cr, uid,
            context), 'datas': pq['datas'], 'nodestroy': True} 
