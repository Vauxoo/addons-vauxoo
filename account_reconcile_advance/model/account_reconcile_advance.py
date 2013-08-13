# -*- encoding: utf-8 -*-
from openerp.osv import osv
from openerp.osv import fields 

class account_reconcile_advance(osv.Model):
    
    '''description'''
    
    _name = 'account.reconcile.advance'
    
    _columns = {
        'name':fields.char('Name', size=256, help='Name of This Advance Document'), 
        'date':fields.date('Date', help='Document Date'), 
        'date_post':fields.date('Accounting Date', help='Date to be used in Journal Entries when posted'), 
        'state':fields.selection([('draft','Draft'),('approved','Approved'),
            ('done','Done')], help='State'), 
        'partner_id':fields.many2one('res.partner', 'Partner', help='Advance Partner'), 
        'period_id':fields.many2one('account.period', 'Accounting Period', help='Period where Journal Entries will be posted'), 
        'journal_id':fields.many2one('account.journal', 'Journal', help='Accounting Journal where Entries will be posted'), 
        'invoice_ids':fields.many2many('account.invoice', 'ara_invoice_rel', 'ara_id', 'inv_id', 'Invoices', help='Invoices to be used in this Advance'), 
        'voucher_ids':fields.many2many('account.voucher', 'ara_voucher_rel', 'ara_id', 'voucher_id', 'Advances', help='Advances to be used'), 
        'ai_aml_ids':fields.many2many('account.move.line', 'ara_ai_aml_rel', 'ara_id', 'aml_id', 'Invoice Entry Lines', help=''), 
        'av_aml_ids':fields.many2many('account.move.line', 'ara_av_aml_rel', 'ara_id', 'aml_id', 'Advance Entry Lines', help=''), 
    }
    _defaults = {
        'state':'draft'        
    }
