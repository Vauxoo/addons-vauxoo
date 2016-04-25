# coding: utf-8
from openerp.osv import fields, osv


class AccountVoucherCategoryType(osv.Model):
    _name = 'account.voucher.category.type'
    _columns = {
        'name': fields.char('Name', 256, help='Type Name', translate=True),
    }


class AccountVoucherCategory(osv.Model):
    _order = "parent_left"
    _parent_order = "code"
    _parent_store = True
    _name = 'account.voucher.category'
    _rec_name = 'complete_name'

    def _get_full_name(self, cr, uid, ids, name=None, args=None, context=None):
        if context == None:
            context = {}
        res = {}
        for elmt in self.browse(cr, uid, ids, context=context):
            user_type = ''
            if elmt.user_type:
                user_type = '[%s] ' % elmt.user_type.name
            res[elmt.id] = user_type + self._get_one_full_name(elmt)
        return res

    def _get_one_full_name(self, elmt, level=6):
        if level <= 0:
            return '...'
        if elmt.parent_id:
            parent_path = self._get_one_full_name(
                elmt.parent_id, level - 1) + " / "
        else:
            parent_path = ''
        return parent_path + elmt.name

    _columns = {
        'name': fields.char('Name', 256, help='Category Name', translate=True),
        'code': fields.char('Code', 64, help='Category Code'),
        'type': fields.selection([('view', 'View'), ('other', 'Regular')], string='Category Type', help='Category Type'),
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'parent_id': fields.many2one('account.voucher.category', 'Parent Category',
                                     ondelete='restrict',
                                     help='Allows to create a Hierachycal Tree of Categories'),
        'parent_left': fields.integer('Parent Left', select=1),
        'parent_right': fields.integer('Parent Right', select=1),
        'complete_name': fields.function(_get_full_name, type='char', string='Full Name'),
        'user_type': fields.many2one('account.voucher.category.type', 'Custom Type', help='Let you define you own Category Type'),
    }

    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
    }

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if context is None:
            context = {}
        ids2 = []
        if name:
            ids = self.search(
                cr, uid, [('code', '=', name)] + args, limit=limit, context=context)
            ids2 = self.search(
                cr, uid, [('user_type', 'ilike', name)] + args, limit=limit, context=context)
            if not ids:
                dom = []
                for name2 in name.split('/'):
                    name = name2.strip()
                    ids = self.search(
                        cr, uid, dom + [('name', 'ilike', name)] + args, limit=limit, context=context)
                    if not ids:
                        break
                    dom = [('parent_id', 'in', ids)]
        else:
            ids = self.search(cr, uid, args, limit=limit, context=context)
        return self.name_get(cr, uid, ids2 + ids, context=context)

    def name_get(self, cr, uid, ids, context=None):
        res = []
        if not ids:
            return res
        if isinstance(ids, (int, long)):
            ids = [ids]
        for id in ids:
            elmt = self.browse(cr, uid, id, context=context)
            user_type = ''
            if elmt.user_type:
                user_type = '[%s] ' % elmt.user_type.name
            res.append((id, user_type + self._get_one_full_name(elmt)))
        return res


class AccountVoucher(osv.Model):
    _inherit = 'account.voucher'

    _columns = {
        'av_cat_id': fields.many2one('account.voucher.category', 'Voucher Category'),
    }

    def first_move_line_get(self, cr, uid, voucher_id, move_id, company_currency, current_currency, context=None):
        """Return a dict to be use to create the first account move line of given voucher.

        :param voucher_id: Id of voucher what we are creating account_move.
        :param move_id: Id of account move where this line will be added.
        :param company_currency: id of currency of the company to which the voucher belong
        :param current_currency: id of currency of the voucher
        :return: mapping between fieldname and value of account move line to create
        :rtype: dict
        """
        context = context or {}
        move_line = super(AccountVoucher, self).first_move_line_get(cr, uid,
                                                                    voucher_id, move_id, company_currency, current_currency,
                                                                    context=context)
        voucher = self.pool.get('account.voucher').browse(
            cr, uid, voucher_id, context)
        move_line['av_cat_id'] = voucher.av_cat_id and voucher.av_cat_id.id or False
        return move_line


class AccountMoveLine(osv.Model):
    _inherit = 'account.move.line'

    _columns = {
        'av_cat_id': fields.many2one('account.voucher.category', 'Voucher Category'),
    }


class ScrvwReportAccountVoucherCategory(osv.Model):

    _name = 'scrvw.report.account.voucher.category'
    _auto = False

    _columns = {
        # size??
        'name': fields.char('Account Move Line Name', readonly=True),
        'debit': fields.float('Debit', readonly=True),
        'credit': fields.float('Credit', readonly=True),
        'balance': fields.float('Balance', help='Debit - Credit', readonly=True),
        'avc_id': fields.many2one(
            'account.voucher.category',
            readonly=True,
            string='Account Voucher Category'),
        'avc_name': fields.char(
            'Account Voucher Cateogry Name',
            readonly=True,
            help='Account Voucher Category Name'),
        'avc_code': fields.char(
            'Account Voucher Category Code',
            readonly=True,
            help='Account Voucher Category Code'),
        'avc_parent_id': fields.many2one(
            'account.voucher.category',
            readonly=True,
            string='Account Voucher Category Parent'),
        'avc_parent_name': fields.char(
            'Account Voucher Cateogry Parent Name',
            readonly=True,
            help='Account Voucher Category Parent Name'),
        'avc_parent_code': fields.char(
            'Account Voucher Category Parent Code',
            readonly=True,
            help='Account Voucher Category Parent Code'),
        'avc_grand_parent_id': fields.many2one(
            'account.voucher.category',
            readonly=True,
            string='Account Voucher Category Grand Parent'),
        'avc_grand_parent_name': fields.char(
            'Account Voucher Cateogry Grand Parent Name',
            readonly=True,
            help='Account Voucher Category Grand Parent Name'),
        'avc_grand_parent_code': fields.char(
            'Account Voucher Category Grand Parent Code',
            readonly=True,
            help='Account Voucher Category Grand Parent Code'),
        'aa_id': fields.many2one(
            'account.analytic.account',
            readonly=True,
            string='Analytic Account'),
        'date': fields.date('Date', readonly=True),
        'account_id': fields.many2one(
            'account.account',
            readonly=True,
            string='Bank Account'),
        'month': fields.integer('Month', readonly=True),
        'period_id': fields.many2one(
            'account.period', string='Fiscal Year Period', readonly=True),
    }

    def init(self, cr):
        query = """
            CREATE OR REPLACE VIEW %s AS (
                SELECT aml.id, aml.name, aml.debit, aml.credit,
                       aml.av_cat_id AS avc_id, avc.code AS avc_code,
                       avc.name AS avc_name,
                       avc.parent_id AS avc_parent_id,
                       avcp.code AS avc_parent_code,
                       avcp.name AS avc_parent_name,
                       avcp.parent_id AS avc_grand_parent_id,
                       avcgp.code AS avc_grand_parent_code,
                       avcgp.name AS avc_grand_parent_name,
                       aml.analytic_account_id AS aa_id,
                       aml.account_id, aml.date,
                       EXTRACT(MONTH FROM date) AS month,
                       aml.period_id, (aml.debit-aml.credit) AS balance
                FROM account_move_line AS aml
                INNER JOIN account_account AS aa ON aml.account_id=aa.id
                INNER JOIN account_voucher_category AS avc
                      ON aml.av_cat_id=avc.id
                INNER JOIN account_voucher_category AS avcp
                      ON avcp.id=avc.parent_id
                LEFT JOIN account_voucher_category AS avcgp
                      ON avcgp.id=avcp.parent_id
                WHERE aa.type = 'liquidity'
            )""" % (self._name.replace('.', '_'))
        cr.execute(query)
