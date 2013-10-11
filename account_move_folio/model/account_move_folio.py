# -*- encoding: utf-8 -*-
from openerp.osv import fields, osv

class account_move_folio(osv.Model):
    _name = 'account.move.folio'
    _description = "Records of Folios in Journal Entries"
    _columns = {
        'name':fields.char('Name', 256, help='Folio Number', required = True), 
        'move_id':fields.many2one('account.move', 'Journal Entry', help='Journal Entry'), 
        'journal_id':fields.many2one('account.journal', 'Journal', help='Entry Journal'), 
        'period_id':fields.many2one('account.period', 'Period', help='Entry Period'), 
        'date':fields.date('Date', help='Entry Date'), 
        'company_id':fields.many2one('res.company', 'Company', help='Entry Company'), 
    }

    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
    }

class account_move(osv.Model):
    _inherit = 'account.move'

    _columns = {
        'folio_id': fields.many2one('account.move.folio', 'Folio Record'),
    }

