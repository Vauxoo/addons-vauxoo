# -*- encoding: utf-8 -*-
from openerp.osv import fields, osv

class account_voucher_category(osv.Model):
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
            res[elmt.id] = self._get_one_full_name(elmt)
        return res

    def _get_one_full_name(self, elmt, level=6):
        if level<=0:
            return '...'
        if elmt.parent_id and not elmt.type == 'template':
            parent_path = self._get_one_full_name(elmt.parent_id, level-1) + " / "
        else:
            parent_path = ''
        return parent_path + elmt.name

    _columns = {
        'name':fields.char('Name', 256, help='Category Name', translate=True), 
        'code':fields.char('Code', 64, help='Category Code'), 
        'type':fields.selection([('view','View'),('other','Regular')], string='Category Type', help='Category Type'), 
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'parent_id':fields.many2one('account.voucher.category', 'Parent Category', 
            ondelete = 'restrict',
            help='Allows to create a Hierachycal Tree of Categories'), 
        'parent_left': fields.integer('Parent Left', select=1),
        'parent_right': fields.integer('Parent Right', select=1),
        'complete_name': fields.function(_get_full_name, type='char', string='Full Name'),
    }

    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
    }

class account_voucher(osv.Model):
    _inherit = 'account.voucher'

    _columns = {
        'av_cat_id': fields.many2one('account.voucher.category', 'Voucher Category'),
    }

    def first_move_line_get(self, cr, uid, voucher_id, move_id, company_currency, current_currency, context=None):
        '''
        Return a dict to be use to create the first account move line of given voucher.

        :param voucher_id: Id of voucher what we are creating account_move.
        :param move_id: Id of account move where this line will be added.
        :param company_currency: id of currency of the company to which the voucher belong
        :param current_currency: id of currency of the voucher
        :return: mapping between fieldname and value of account move line to create
        :rtype: dict
        '''
        context = context or {}
        move_line = super(account_voucher, self).first_move_line_get(cr, uid,
                voucher_id, move_id, company_currency, current_currency,
                context=context)
        voucher = self.pool.get('account.voucher').browse(cr,uid,voucher_id,context)
        move_line['av_cat_id'] = voucher.av_cat_id and voucher.av_cat_id.id or False
        return move_line


class account_move_line(osv.Model):
    _inherit = 'account.move.line'

    _columns = {
        'av_cat_id': fields.many2one('account.voucher.category', 'Voucher Category'),
    }
