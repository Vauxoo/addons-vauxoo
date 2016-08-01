# coding: utf-8
from openerp import models, fields, api, _
from openerp.tools.safe_eval import safe_eval
from . import rst2html


class HrTimesheetReportsBase(models.Model):

    _name = "project.report"
    _inherit = ['mail.thread']

    @api.one
    @api.depends('comment_timesheet',
                 'comment_invoices',
                 'comment_issues',
                 'comment_hu')
    def _comment2html(self):
        self.cts2html = rst2html.html.rst2html(self.comment_timesheet)
        self.ci2html = rst2html.html.rst2html(self.comment_invoices)
        self.ciss2html = rst2html.html.rst2html(self.comment_issues)
        self.chu2html = rst2html.html.rst2html(self.comment_hu)

    name = fields.Char('Report Title')
    comment_invoices = fields.Text(
        'Comment about Invoices',
        help="It will appear just above list of invoices.")
    ci2html = fields.Text(
        'Comments Invoices html', compute='_comment2html',
        help='It will appear just above the resumed timesheets.')
    comment_timesheet = fields.Text(
        'Comment about Timesheets',
        help='It will appear just above the resumed timesheets.')
    cts2html = fields.Text(
        'Comments TS html', compute='_comment2html',
        help='It will appear just above the resumed timesheets.')
    comment_issues = fields.Text(
        'Comment about Timesheets',
        help='It will appear just above the resumed issues.')
    ciss2html = fields.Text(
        'Comments Issues html', compute='_comment2html',
        help='It will appear just above the resumed timesheets.')
    comment_hu = fields.Text(
        'Comment about Timesheets',
        help='It will appear just above the resumed hu status.')
    chu2html = fields.Text('Comments User Stories html',
                           compute='_comment2html',
                           help='It will appear just above '
                           'the resumed timesheets.')
    user_id = fields.Many2one(
        'res.users', 'Responsible',
        help='Owner of the report, generally the person that create it.')
    partner_id = fields.Many2one(
        'res.partner', 'Contact',
        help='Contact which you will send this report.')
    filter_hu_id = fields.Many2one(
        'ir.filters', 'User Stories',
        domain=[('model_id', '=', 'user.story')],
        context={'default_model_id': 'user.story'},
        help='Set the filter for issues TIP = go to issues and look for '
        'the filter that adjust to your needs of issues to be shown.')
    filter_issue_id = fields.Many2one(
        'ir.filters', 'Issues',
        domain=[('model_id', '=', 'project.issue')],
        context={'default_model_id': 'project.issue'},
        help='Set the filter for issues TIP = go to issues and look for '
        ' the filter that adjust to your needs of issues to be shown.')
    filter_invoice_id = fields.Many2one(
        'ir.filters', 'Invoices',
        domain=[('model_id', '=', 'account.invoice')],
        context={'default_model_id': 'account.invoice'},
        help='Filter of Invoices to be shown TIP = '
        'Go to Accounting/Customer '
        'Invoices in order to create the filter you want to show on this'
        'report.',)
    filter_id = fields.Many2one(
        'ir.filters', 'Filter',
        domain=[('model_id', '=', 'hr.analytic.timesheet')],
        context={'default_model_id': 'hr.analytic.timesheet'},
        help="Filter should be by date, group_by is ignored, the model which "
             "the filter should belong to is timesheet.")
    show_details = fields.Boolean('Show Detailed Timesheets')
    # records = fields.Text('Records', compute='_get_print_data',)
    state = fields.Selection(
        [('draft', 'Draft'), ('sent', 'Sent')], 'Status',
        help='Message sent already to customer (it will block edition)')
    company_id = fields.Many2one(
        'res.company', 'Company', help='Company which this report belongs to')
    product_id = fields.Many2one(
        'product.product', 'Product to Compute Totals',
        help='This product will be used to compute totals')
    currency_id = fields.Many2one(
        'res.currency', 'Currency',
        help='This product will be used to compute totals')
    prod_ent_ids = fields.Many2many(
        'product.product', 'prod_report_timesheet_rel1', 'report_id',
        'prod_ent_id', 'Products for Enterprises',
        help="All lines on invoices the have this product will be ignored as "
             "Effectivally Invoiced time already invoiced")
    prod_train_ids = fields.Many2many(
        'product.product', 'prod_report_timesheet_rel2', 'report_id',
        'prod_train_id', 'Products for Training',
        help="All lines that have this products will Be ignored due to this is"
             " just for products")
    prod_cons_ids = fields.Many2many(
        'product.product', 'prod_report_timesheet_rel3', 'report_id',
        'prod_cons_id', 'Products for Consultancy',
        help="All products here will be considered as consultancy then it will"
             "be compared by currency and by considering the product in this "
             "reports to use the unit_price and the currency")

    def do_report(self):
        return self.env['report'].get_action(
            'hr_timesheet_reports.', 'timesheet_report_vauxoo')

    # def go_to_timesheet(self, cr, uid, ids, context=None):
    #     if context is None:
    #         context = {}
    #     report = self.browse(cr, uid, ids, context=context)[0]
    #     context.update({
    #         'ts_report_id': ids[0],
    #     })
    #     return {'type': 'ir.actions.act_window',
    #             'res_model': 'hr.analytic.timesheet',
    #             'name': 'Timesheet Activities Reported',
    #             'view_type': 'form',
    #             'view_mode': 'tree,form',
    #             'domain': report.filter_id.domain,
    #             'context': context,
    #             }

    # def go_to_invoices(self, cr, uid, ids, context=None):
    #     if context is None:
    #         context = {}
    #     report = self.browse(cr, uid, ids, context=context)[0]
    #     context.update({
    #         'ts_report_id': ids[0],
    #     })
    #     return {'type': 'ir.actions.act_window',
    #             'res_model': 'account.invoice',
    #             'name': 'Invoices Reported',
    #             'view_type': 'form',
    #             'view_mode': 'tree,form',
    #             'domain': report.filter_invoice_id.domain,
    #             'context': context,
    #             }

    # def go_to_issues(self, cr, uid, ids, context=None):
    #     if context is None:
    #         context = {}
    #     report = self.browse(cr, uid, ids, context=context)[0]
    #     context.update({
    #         'ts_report_id': ids[0],
    #     })
    #     return {'type': 'ir.actions.act_window',
    #             'res_model': 'project.issue',
    #             'name': 'Issues Reported',
    #             'view_type': 'form',
    #             'view_mode': 'tree,form',
    #             'domain': report.filter_issue_id.domain,
    #             'context': context,
    #             }

    # def go_to_hu(self, cr, uid, ids, context=None):
    #     if context is None:
    #         context = {}
    #     report = self.browse(cr, uid, ids, context=context)[0]
    #     context.update({
    #         'ts_report_id': ids[0],
    #     })
    #     return {'type': 'ir.actions.act_window',
    #             'res_model': 'user.story',
    #             'name': 'User Stories Reported',
    #             'view_type': 'form',
    #             'view_mode': 'tree,form',
    #             'domain': report.filter_hu_id.domain,
    #             'context': context,
    #             }

    def clean_timesheet(self, cr, uid, ids, context=None):
        """To be sure all timesheet lines are at least setted as billable
        100% in order to show correct first approach of numbers.
        """
        timesheet_obj = self.pool.get('hr.analytic.timesheet')
        report = self.browse(cr, uid, ids, context=context)[0]
        domain = report.filter_id.domain
        dom = [len(d) > 1 and tuple(d) or d for d in safe_eval(domain)]
        timesheet_ids = timesheet_obj.search(cr, uid,
                                              dom + [('to_invoice', '=', False)],  # noqa
                                              context=context)  # noqa
        # By default 100% wired to the one by default in db.
        # If you want another one overwrite this method or change the
        # rate on such record.
        timesheet_obj.write(cr, uid,
                            timesheet_ids,
                            {'to_invoice': 1},
                            context=context)
        return True
