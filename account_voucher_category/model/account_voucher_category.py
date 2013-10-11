# -*- encoding: utf-8 -*-
from openerp.osv import fields, osv

class account_voucher_category(osv.Model):
    _order = "parent_left"
    _parent_order = "code"
    _parent_store = True
    _name = 'account.voucher.category'

    _columns = {
        'name':fields.char('Name', 256, help='Category Name'), 
        'code':fields.char('Code', 64, help='Category Code'), 
        'type':fields.selection([('view','View'),('other','Regular')], string='Category Type', help='Category Type'), 
        'parent_id':fields.many2one('account.voucher.category', 'Parent Category', 
            help='Allows to create a Hierachycal Tree of Categories'), 
        'parent_left': fields.integer('Parent Left', select=1),
        'parent_right': fields.integer('Parent Right', select=1),
    }

class account_voucher(osv.Model):
    _inherit = 'account.voucher'

    _columns = {
        'av_cat_id': fields.many2one('account.voucher.category', 'Voucher Category'),
    }

class account_move_line(osv.Model):
    _inherit = 'account.move.line'

    _columns = {
        'av_cat_id': fields.many2one('account.voucher.category', 'Voucher Category'),
    }
