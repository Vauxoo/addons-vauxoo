# -*- encoding: utf-8 -*-
from openerp.osv import fields, osv

class account_move_folio(osv.Model):
    _name = 'account.move.folio'
    _description = "Records of Folios in Journal Entries"
    _columns = {
        'name':fields.char('Folio', 256, help='Folio Number', required = True), 
        'move_id':fields.many2one('account.move', 'Journal Entry', help='Journal Entry'), 
        'journal_id':fields.many2one('account.journal', 'Journal', help='Entry Journal'), 
        'period_id':fields.many2one('account.period', 'Period', help='Entry Period'), 
        'date':fields.date('Date', help='Entry Date'), 
        'company_id':fields.many2one('res.company', 'Company', help='Entry Company'), 
        'move_state':fields.related('move_id','state', type='selection',
            selection=[('draft','Unposted'), ('posted','Posted')], store=True,
            string='Entry State', help='Entry State'), 
        'period_state':fields.related('period_id','state', type='selection',
            selection=[('draft','Open'), ('done','Closed')], store=True,
            string='Period State', help='Period State'), 
    }

    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
    }

class account_move(osv.Model):
    _inherit = 'account.move'

    _columns = {
        'folio_id': fields.many2one('account.move.folio', 'Folio Record'),
    }

    def foliate(self, cr, uid, ids, context=None):
        context = context or {}
        folio_obj = self.pool.get('account.move.folio')
        invoice = context.get('invoice', False)
        for move in self.browse(cr, uid, ids, context=context):
            if not move.folio_id:
                values = {
                    'name': move.name,
                    'move_id': move.id,
                    'journal_id': move.journal_id.id,
                    'period_id': move.period_id.id,
                    'date': move.date,
                }
                if invoice:
                    folio_ids = folio_obj.search(cr, uid,
                            [('name','=',move.name),
                                ('journal_id','=',move.journal_id.id),
                                ('company_id','=',move.company_id.id)],
                            context=context)
                    if folio_ids:
                        folio_id = folio_ids[0]
                        folio_obj.write(cr, uid, folio_id, values, context=context)
                    else:
                        folio_id = folio_obj.create(cr, uid, values,context=context)
                else:
                    folio_id = folio_obj.create(cr, uid, values,context=context)
                move.write({'folio_id':folio_id},context=context)
        return True
    
    def post(self, cr, uid, ids, context=None):
        context = context or {}
        super(account_move, self).post(cr, uid, ids, context=context)
        self.foliate(cr, uid, ids, context=context)
        return True

