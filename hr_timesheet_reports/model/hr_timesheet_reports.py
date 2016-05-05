# coding: utf-8
from openerp import models, fields, api, _
from openerp.tools.safe_eval import safe_eval
from openerp import SUPERUSER_ID
from . import rst2html

import re


def clean_name(name):
    exp = r'\[.*?\]'
    text = name.strip()
    found = re.findall(exp, text)
    if found:
        for fou in found:
            text = text.replace(fou, '').strip()
    words = text.split(' ')
    if len(words) > 2:
        text = ' '.join([words[0], words[2]])
    return text


class HrTimesheetReportsBase(models.Model):

    _name = "hr.timesheet.reports.base"
    _inherit = ['mail.thread']

    def _prepare_data(self, cr, uid, ids, record, context=None):
        line_id = record.line_id and record.line_id.id or "NO-LINE"
        invoice_id = record.line_id and record.line_id.invoice_id
        work_ids, issue_ids = [], []
        if isinstance(line_id, int):
            work_obj = self.pool.get('project.task.work')
            issue_obj = self.pool.get('project.issue')
            work_ids = work_obj.search(cr, uid,
                                       [('hr_analytic_timesheet_id',
                                         '=', record.id)], context=context)
            work_brw = work_obj.browse(cr, uid,
                                       work_ids,
                                       context=context)[0]
            issue_ids = issue_obj.search(cr, uid,
                                         [('task_id',
                                           '=', work_brw.task_id.id)],
                                         context=context)
        return {'author': clean_name(record.user_id.name),
                'description': record.name,
                'duration': record.unit_amount,
                'invoiceables_hours': record.invoiceables_hours,
                'to_invoice': record.to_invoice,
                'date': record.date,
                'analytic': record.account_id.name,
                'issue': ' '.join([str(i) for i in issue_ids]),
                'line': line_id,
                'invoice_id': invoice_id,
                'task_id': work_brw.task_id,
                'record': record,
                'id': record.id}

    def _get_print_data(self, cr, uid, ids, name, args, context=None):
        res = {}
        for wzd in self.browse(cr, uid, ids, context=context):
            res[wzd.id] = self._get_result_ids(cr, uid, ids, context=context)
        return res

    def _get_total_time(self, grouped, field):
        total_list = [g[field] for g in grouped]
        return sum(total_list)

    def _get_report_inv(self, cr, uid, ids, context=None):
        invoice_obj = self.pool.get('account.invoice')
        wzr_brw = self.browse(cr, uid, ids, context=context)[0]
        domain_inv = wzr_brw.filter_invoice_id and \
            wzr_brw.filter_invoice_id.domain or []
        if not domain_inv:
            return ([], [], [], [], {})
        dom_inv = [len(d) > 1 and tuple(d) or d for d in safe_eval(domain_inv)]
        # Preparing grouped invoices due to it is 2 levels it need a
        # little extra Work.
        elements = invoice_obj.read_group(cr, uid, dom_inv,
                                          ['period_id',
                                           'amount_total',
                                           'amount_tax',
                                           'amount_untaxed',
                                           'residual',
                                           'partner_id'
                                           ],
                                          ['period_id',
                                           'amount_total',
                                           'amount_tax',
                                           'amount_untaxed',
                                           'residual',
                                           ],
                                          context=context)
        grouped_by_currency = invoice_obj.read_group(cr, uid, dom_inv,
                                                     ['currency_id',
                                                      'amount_total',
                                                      'amount_tax',
                                                      'amount_untaxed',
                                                      'residual',
                                                      'partner_id'
                                                      ],
                                                     ['currency_id',
                                                      'amount_total',
                                                      'amount_tax',
                                                      'amount_untaxed',
                                                      'residual',
                                                      ],
                                                     context=context)
        inv_line_obj = self.pool.get('account.invoice.line')
        curr_obj = self.pool.get('res.currency')
        grouped_by_product = {}
        ent_ids = [ent.id for ent in wzr_brw.prod_ent_ids]
        train_ids = [ent.id for ent in wzr_brw.prod_train_ids]
        cons_ids = [ent.id for ent in wzr_brw.prod_cons_ids]
        all_ids = ent_ids + cons_ids + train_ids
        for gbc in grouped_by_currency:
            currency = gbc['currency_id']
            inv_line_ids = invoice_obj.search(
                cr, uid, dom_inv + [('currency_id', 'in', [currency[0]])],
                context=context)
            group_prod = inv_line_obj.read_group(
                cr, uid, [('invoice_id', 'in', inv_line_ids)],
                ['product_id', 'price_subtotal', ],
                ['product_id', 'price_subtotal', ], context=context)
            total_ent = sum([gr['price_subtotal'] for gr in group_prod
                             if gr['product_id'][0] in ent_ids])
            total_cons = sum([gr['price_subtotal'] for gr in group_prod
                              if gr['product_id'][0] in cons_ids])
            total_train = sum([gr['price_subtotal'] for gr in group_prod
                               if gr['product_id'][0] in train_ids])
            total_others = sum([gr['price_subtotal'] for gr in group_prod
                                if gr['product_id'][0] not in all_ids])
            total = total_ent + total_ent + total_train + total_others
            curr_from = wzr_brw.currency_id.id
            curr_to = currency[0]
            curr_from_brw = curr_obj.browse(cr, uid, curr_from,
                                            context=context)
            curr_to_brw = curr_obj.browse(cr, uid, curr_to, context=context)
            rate = curr_obj._get_conversion_rate(cr, uid,
                                                 curr_from_brw,
                                                 curr_to_brw,
                                                 context=context)
            grouped_by_product[gbc['currency_id'][1]] = {
                'enterprises': total_ent,
                'consultancy': total_cons,
                'others': total_others,
                'training': total_train,
                'pending': total_train,
                'total': total,
                'rate': rate,
                'total_in_control': round(total / rate, 2),
                'total_cons': round(total_cons / rate, 2),
                'total_train': round(total_train / rate, 2),
                'total_others': round(total_others / rate, 2),
                'total_lic': round(total_ent / rate, 2),
                'conversion_rate': curr_obj._get_conversion_rate(
                    cr, uid, curr_obj.browse(cr, uid, curr_from,
                                             context=context),
                    curr_obj.browse(cr, uid, curr_to, context=context)),
            }
        #  TODO: This must be a better way to achieve this list directly from
        #  search group on v8.0 for now the simplest way make a list with
        #  everything an group in the report itself
        invoice_ids = invoice_obj.search(cr, uid, dom_inv, context=context)
        invoices_brw = invoice_obj.browse(cr, uid, invoice_ids,
                                          context=context)
        # Getting resumed numbers
        resumed_numbers = {
            'total_invoiced': sum([grouped_by_product[i]['total_in_control']
                                   for i in grouped_by_product])
        }
        return (elements, grouped_by_currency,
                invoices_brw, grouped_by_product,
                resumed_numbers)

    def _get_report_hus(self, cr, uid, ids, context=None):
        hu_obj = self.pool.get('user.story')
        wzr_brw = self.browse(cr, uid, ids, context=context)[0]
        domain_hu = wzr_brw.filter_hu_id and wzr_brw.filter_hu_id.domain or []
        if not domain_hu:
            return []
        dom_hu = [len(d) > 1 and tuple(d) or d for d in safe_eval(domain_hu)]
        # Setting the HU elements
        hu_ids = hu_obj.search(cr, uid, dom_hu,
                               order='state asc', context=context)
        hu_brw = hu_obj.browse(cr, uid, hu_ids, context=context)
        return hu_brw

    def _get_report_issue(self, cr, uid, ids, context=None):
        issue_obj = self.pool.get('project.issue')
        wzr_brw = self.browse(cr, uid, ids, context=context)[0]
        domain_issues = wzr_brw.filter_issue_id and \
            wzr_brw.filter_issue_id.domain or []
        if not domain_issues:
            return []
        dom_issues = [len(d) > 1 and tuple(d) or d
                      for d in safe_eval(domain_issues)]
        # Setting issues elements.
        issues_grouped = issue_obj.read_group(cr, uid, dom_issues,
                                              ['analytic_account_id'],
                                              ['analytic_account_id'],
                                              context=context)

        issues_all = []
        for issue in issues_grouped:
            analytic_id = issue.get('analytic_account_id')
            new_issue_dom = dom_issues + [('analytic_account_id', '=', analytic_id and analytic_id[0] or analytic_id)]  # noqa
            issue['children_by_stage'] = issue_obj.read_group(cr, uid, new_issue_dom,  # noqa
                                                              ['stage_id'],
                                                              ['stage_id'],
                                                              orderby='stage_id asc',  # noqa
                                                              context=context)
            issues_all.append(issue)
        return issues_all

    def _get_report_ts(self, cr, uid, ids, context=None):
        timesheet_obj = self.pool.get('hr.analytic.timesheet')
        wzr_brw = self.browse(cr, uid, ids, context=context)[0]
        domain = wzr_brw.filter_id.domain
        dom = [len(d) > 1 and tuple(d) or d for d in safe_eval(domain)]
        timesheet_ids = timesheet_obj.search(cr, uid, dom,
                                             order='account_id asc, user_id asc, date asc',  # noqa
                                             context=context)
        # Group elements
        res = []
        timesheet_brws = timesheet_obj.browse(cr, uid, timesheet_ids,
                                              context=context)
        res_result = [self._prepare_data(cr, uid, ids, tb, context=context) for tb in timesheet_brws]  # noqa
        res = sorted(res_result, key=lambda k: k['issue'], reverse=True)
        grouped = timesheet_obj.read_group(cr, uid, dom,
                                           ['account_id',
                                            'unit_amount',
                                            'invoiceables_hours'],
                                           ['account_id'],
                                           context=context)
        grouped_month = timesheet_obj.read_group(cr, uid, dom,
                                                 ['date',
                                                  'account_id',
                                                  'unit_amount',
                                                  'invoiceables_hours'],
                                                 ['date'],
                                                 context=context)
        grouped_by_user = timesheet_obj.read_group(cr, uid, dom,
                                                   ['user_id',
                                                    'unit_amount',
                                                    'invoiceables_hours'],
                                                   ['user_id'],
                                                   context=context)
        # Separate per project (analytic)
        projects = set([l['analytic'] for l in res])
        return (grouped, grouped_month, projects, res, grouped_by_user)

    def _get_total_inv_amount(self, cr, uid, ids, grouped, context=None):
        pending = sum([gro['invoiceables_hours'] for gro in grouped])
        pending_inv = round(
            pending * self.browse(
                cr, uid, ids, context=context)[0].product_id.list_price, 2)
        return pending_inv

    def _get_result_ids(self, cr, uid, ids, context=None):
        uid = SUPERUSER_ID
        gi, gbc, ibrw, gbp, rn = self._get_report_inv(cr, uid, ids, context=context)  # noqa
        grouped, gbm, projects, res, gbu = self._get_report_ts(cr, uid,
                                                               ids, context=context)  # noqa
        rn['pending'] = self._get_total_inv_amount(cr, uid, ids, grouped, context)  # noqa
        info = {
            'data': {},
            'resume': grouped,
            'resume_month': gbm,
            'resume_user': gbu,
            'resume_product': gbp,
            'invoices': ibrw,
            'issues': self._get_report_issue(cr, uid,
                                             ids, context=context),
            'user_stories': self._get_report_hus(cr, uid,
                                                 ids, context=context),
            'total_ts_bill_by_month': self._get_total_time(grouped,
                                                           'invoiceables_hours'),  # noqa
            'total_ts_by_month': self._get_total_time(grouped,
                                                      'unit_amount'),
            'periods': gi,
            'total_invoices': gbc,
            'resumed_numbers': rn,
        }
        for proj in projects:
            info['data'][proj] = [r for r in res if r['analytic'] == proj]
        return info

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
    comment_invoices = fields.Text('Comment about Invoices',
                                   help="It will appear just above "
                                   "list of invoices.")
    ci2html = fields.Text('Comments Invoices html',
                          compute='_comment2html',
                          help='It will appear just above '
                          'the resumed timesheets.')
    comment_timesheet = fields.Text('Comment about Timesheets',
                                    help='It will appear just above '
                                    'the resumed timesheets.')
    cts2html = fields.Text('Comments TS html',
                           compute='_comment2html',
                           help='It will appear just above '
                           'the resumed timesheets.')
    comment_issues = fields.Text('Comment about Timesheets',
                                 help='It will appear just above '
                                 'the resumed issues.')
    ciss2html = fields.Text('Comments Issues html',
                            compute='_comment2html',
                            help='It will appear just above '
                            'the resumed timesheets.')
    comment_hu = fields.Text('Comment about Timesheets',
                             help='It will appear just above '
                             'the resumed hu status.')
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
        domain=[('model_id', 'ilike', 'user.story')],
        help='Set the filter for issues TIP = go to issues and look for '
        'the filter that adjust to your needs of issues to be shown.')
    filter_issue_id = fields.Many2one(
        'ir.filters', 'Issues',
        domain=[('model_id', 'ilike', 'project.issue')],
        help='Set the filter for issues TIP = go to issues and look for '
        ' the filter that adjust to your needs of issues to be shown.')
    filter_invoice_id = fields.Many2one(
        'ir.filters', 'Invoices',
        domain=[('model_id', 'ilike', 'account.invoice')],
        help='Filter of Invoices to be shown TIP = '
        'Go to Accounting/Customer '
        'Invoices in order to create the filter you want to show on this'
        'report.',)
    filter_id = fields.Many2one('ir.filters', 'Filter',
                                domain=[
                                    ('model_id', 'ilike', 'hr.analytic.timesheet')],
                                help="Filter should be by date, group_by is ignored, the model "
                                "which the filter should belong to is timesheet.")
    show_details = fields.Boolean('Show Detailed Timesheets')
    records = fields.Text('Records', compute='_get_print_data',)
    state = fields.Selection([('draft', 'Draft'), ('sent', 'Sent')], 'Status',
                             help='Message sent already to customer (it will block edition)')
    company_id = fields.Many2one(
        'res.company', 'Company', help='Company which this report belongs to')
    product_id = fields.Many2one(
        'product.product', 'Product to Compute Totals', help='This product will be used to compute totals')
    currency_id = fields.Many2one(
        'res.currency', 'Currency', help='This product will be used to compute totals')
    prod_ent_ids = fields.Many2many('product.product', 'prod_report_timesheet_rel1', 'report_id', 'prod_ent_id', 'Products for Enterprises',
                                    help="All lines on invoices the "
                                    "have this product will "
                                    "be ignored as Effectivally "
                                    "Invoiced time already invoiced")
    prod_train_ids = fields.Many2many('product.product',
                                      'prod_report_timesheet_rel2',
                                      'report_id', 'prod_train_id',
                                      'Products for Training',
                                      help="All lines that have this "
                                      "products will "
                                      "Be ignored due to this is just "
                                      "for products")
    prod_cons_ids = fields.Many2many('product.product',
                                     'prod_report_timesheet_rel3',
                                     'report_id', 'prod_cons_id',
                                     'Products for Consultancy',
                                     help="All products here will be "
                                     "considered as consultancy"
                                     "then it will be compared by "
                                     "currency and by "
                                     "considering the product "
                                     "in this reports to use "
                                     "the unit_price and the currency")

    _defaults = {
        'state': lambda * a: 'draft',
        'user_id': lambda obj, cr, uid, context: uid,
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'sale.shop', context=c),  # noqa
    }

    def do_report(self, cr, uid, ids, context=None):
        return self.pool['report'].\
            get_action(cr, uid, ids, 'hr_timesheet_reports.'
                       'timesheet_report_vauxoo', context=context)

    def go_to_timesheet(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        report = self.browse(cr, uid, ids, context=context)[0]
        context.update({
            'ts_report_id': ids[0],
        })
        return {'type': 'ir.actions.act_window',
                'res_model': 'hr.analytic.timesheet',
                'name': 'Timesheet Activities Reported',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'domain': report.filter_id.domain,
                'context': context,
                }

    def go_to_invoices(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        report = self.browse(cr, uid, ids, context=context)[0]
        context.update({
            'ts_report_id': ids[0],
        })
        return {'type': 'ir.actions.act_window',
                'res_model': 'account.invoice',
                'name': 'Invoices Reported',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'domain': report.filter_invoice_id.domain,
                'context': context,
                }

    def go_to_issues(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        report = self.browse(cr, uid, ids, context=context)[0]
        context.update({
            'ts_report_id': ids[0],
        })
        return {'type': 'ir.actions.act_window',
                'res_model': 'project.issue',
                'name': 'Issues Reported',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'domain': report.filter_issue_id.domain,
                'context': context,
                }

    def go_to_hu(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        report = self.browse(cr, uid, ids, context=context)[0]
        context.update({
            'ts_report_id': ids[0],
        })
        return {'type': 'ir.actions.act_window',
                'res_model': 'user.story',
                'name': 'User Stories Reported',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'domain': report.filter_hu_id.domain,
                'context': context,
                }

    def send_by_email(self, cr, uid, ids, context=None, cdsm=None):
        ir_model_data = self.pool.get('ir.model.data')
        try:
            template_id = ir_model_data.get_object_reference(cr, uid, 'hr_timesheet_reports', 'email_reports_base')[1]  # noqa
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]  # noqa
        except ValueError:
            compose_form_id = False
        ctx = dict(context)
        ctx.update({
            'default_model': 'hr.timesheet.reports.base',
            'default_res_id': ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    def mark_timesheet(self, cr, uid, ids, context=None):
        return True

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
