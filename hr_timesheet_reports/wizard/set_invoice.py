# coding: utf-8
from openerp.osv import osv, fields


class SetInvoice(osv.osv_memory):

    _name = 'set.invoice'

    def default_get(self, cr, uid, field, context=None):
        if context is None:
            context = {}
        htr = False
        res = super(SetInvoice, self).default_get(
            cr, uid, field, context=context)
        ids = context.get('active_ids', False)
        model = context.get('active_model', False)
        report_id = context.get('ts_report_id', False)
        if report_id:
            htr_obj = self.pool.get('hr.timesheet.reports.base')
            htr = htr_obj.browse(cr, uid, report_id, context=context)
        obj = self.pool.get(model)
        brws = obj.browse(cr, uid, ids, context=context)
        total_h = sum(
            [b.invoiceables_hours for b in brws if b.invoiceables_hours])
        res.update({
            'total_timesheet': total_h,
            'total_money': htr and total_h * htr.product_id.list_price or 0.00,
            'currency_id': htr and htr.currency_id.id,
        })

        return res

    _columns = {
        'total_timesheet': fields.float('Total Timesheet to set',
                                        help="This will be the quantity to "
                                        "be setted to this invoice be sure "
                                        "quantities are consistent"),
        'total_money': fields.float('Total Timesheet in Money',
                                    help="Total in money with the currency and"
                                    "product of the report which you comes "
                                    "from"),
        'currency_id': fields.many2one('product.product', 'Currency',
                                       help='Currency on report')
    }
