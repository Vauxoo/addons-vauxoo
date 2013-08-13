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

class account_voucher(osv.Model):
    _inherit = 'account.voucher'

    def _get_advance(self, cr, uid, ids, name, args, context=None):
        '''
        Check if there is at least one payable or receivable line not
        reconciled at all, if so it will be regarded as an advance
        '''
        context = context or {}
        res = {}.fromkeys(ids,False)
        for av_brw in self.browse(cr, uid, ids, context=context):
            if av_brw.state != 'posted': continue
            i = [l.reconcile_id and True or l.reconcile_partial_id and True or False 
                    for l in av_brw.move_ids 
                        if l.account_id.type in ('receivable','payable')]
            res[av_brw.id] = not all(i) if i else False
        return res

    def _get_voucher_advance(self, cr, uid, ids, context=None):
        context = context or {}
        res = set()
        aml_obj = self.pool.get('account.move.line')
        for l in aml_obj.browse(cr, uid, ids, context=context):
            if not l.move_id: continue
            res.add(l.move_id.id)
        res = list(res)

        if not res: return []

        av_obj = self.pool.get('account.voucher')
        return av_obj.search(cr, uid, [('move_id','in',res)],context=context)

    _columns = {
        'advance':fields.function(_get_advance, method=True, string='Is an Advance?',
        store={
            'account.voucher':(lambda s,c,u,ids,cx:ids,['move_ids','move_id','state'],15),
            'account.move.line':(_get_voucher_advance,['reconcile_id','reconcile_partial_id'],30)
            },
        help='If the payable or receivable are not fully reconcile then it is advance', 
        type='boolean')
    }
