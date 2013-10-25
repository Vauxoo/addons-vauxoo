#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Julio Cesar Serna Hernandez(julio@vauxoo.com)
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
################################################################################
import time
from openerp.osv import fields, osv
from openerp import netsvc
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _


class account_voucher_tax_sat(osv.Model):
    
    _name = 'account.voucher.tax.sat'
    
    _columns = {
        'name': fields.char('Name', size=128,
                            help='Name of This Document',
                            ),
        'partner_id': fields.many2one('res.partner', 'Partner',
                            domain = "[('sat', '=', True)]",
                            help='Partner of SAT',
                            ),
        'date': fields.date('Accounting Date',
                            help='Accounting date affected',
                            ),
        'aml_ids': fields.many2many('account.move.line', 'voucher_tax_sat_rel',
                            'voucher_tax_sat_id', 'move_line_id',
                            'Move Lines', help='Entries to close',
                            ),
        'journal_id':fields.many2one('account.journal', 'Journal',
                            help='Accounting Journal where Entries will be posted',
                            ), 
        'move_id': fields.many2one('account.move', 'Journal Entry',
                            help='Accounting Entry'),
        'company_id':fields.many2one('res.company', 'Company', help='Company'), 
        'period_id': fields.many2one('account.period', 'Period', required=True,
                            help='Period of Entries to find',
                            ),
        'state': fields.selection([
            ('draft', 'New'),
            ('cancelled', 'Cancelled'),
            ('done', 'Done')],
            'Status', readonly=True, track_visibility='onchange'),
    }
    _defaults = {
        'company_id': lambda s, c, u, cx: s.pool.get('res.users').browse(c, u,
            u, cx).company_id.id,
        'state': 'draft'
    }
    
    def onchange_period(self, cr, uid, ids, period, context=None):
        res = {}
        if period:
            res['value'] = {'aml_ids': []}
        return res

    def validate_move_line(self, cr, uid, voucher_tax, context=None):
        move_line_obj = self.pool.get('account.move.line')
        cr.execute(""" SELECT DISTINCT move_line_id FROM voucher_tax_sat_rel
                        WHERE voucher_tax_sat_id <> %s
                        AND move_line_id IN %s """,(
                            voucher_tax.id,
                            tuple([ move_lines.id\
                                    for move_lines in voucher_tax.aml_ids ]))
                    )
        dat = cr.dictfetchall()
        move_line_tax = list( set([ move_tax['move_line_id'] for move_tax in dat ]) )
        if dat:
            raise osv.except_osv(_('Warning'),
                _("You have this jornal items in other voucher tax sat '%s' ")
                % ([ move_line.name\
                        for move_line in move_line_obj.browse(cr, uid,
                                            move_line_tax, context=context)]))

        return True
    
    def action_close_tax(self, cr, uid, ids, context=None):
        aml_obj = self.pool.get('account.move.line')
        period_obj = self.pool.get('account.period')
        context = context or {}
        ids= isinstance(ids,(int,long)) and [ids] or ids
        for voucher_tax_sat in self.browse(cr, uid, ids, context=context):
                                            
                self.validate_move_line(cr, uid,
                                        voucher_tax_sat, context=context)
                                    
                move_id = self.create_move_sat(cr, uid, ids, context=context)
                self.write(cr, uid, ids, {'move_id': move_id})
                
                amount_tax_sat = sum([move_line_tax_sat.credit
                            for move_line_tax_sat in voucher_tax_sat.aml_ids])
                            
                self.create_move_line_sat(cr, uid, voucher_tax_sat,
                                            amount_tax_sat, context=context)
                                            
                self.create_entries_tax_iva_sat(cr, uid, voucher_tax_sat,
                                                            context=context)
                                        
                move_line_copy = [ aml_obj.copy(cr, uid, move_line_tax.id,
                    {
                        'move_id': move_id,
                        'period_id': period_obj.find(cr, uid,
                                        voucher_tax_sat.date,
                                        context=context)[0],
                        'journal_id': voucher_tax_sat.journal_id.id,
                        'credit': 0.0,
                        'debit': move_line_tax.credit,
                        'amount_base': None,
                        'tax_id_secondary': None,
                        'not_move_diot': True
                    }) for move_line_tax in voucher_tax_sat.aml_ids ]
                    
                cr.execute('UPDATE account_move_line '\
                            'SET amount_tax_unround = null '\
                            'WHERE id in %s ',(tuple(move_line_copy), ))
                            
        return self.write(cr, uid, ids, {'state': 'done'}, context=context)
    
    def action_cancel(self, cr, uid, ids, context=None):
        obj_move_line = self.pool.get('account.move.line')
        obj_move = self.pool.get('account.move')
        for tax_sat in self.browse(cr, uid, ids, context=context):
            if tax_sat.move_id:
                obj_move_line._remove_move_reconcile(cr, uid,
                    [move_line.id
                        for move_line in tax_sat.move_id.line_id],
                    context=context)
                obj_move.unlink(cr, uid, [tax_sat.move_id.id],
                                context=context)
        return self.write(cr, uid, ids, {'state': 'draft'}, context=context)
    
    def create_entries_tax_iva_sat(self, cr, uid, voucher_tax_sat,
                                                            context=None):
        aml_obj = self.pool.get('account.move.line')
        av_obj = self.pool.get('account.voucher')
        period_obj = self.pool.get('account.period')
        for move_line in voucher_tax_sat.aml_ids:
            if move_line.tax_id_secondary and\
                                        move_line.tax_id_secondary.tax_sat_ok:
                amount_base, tax_secondary = av_obj._get_base_amount_tax_secondary(cr,
                            uid, move_line.tax_id_secondary,
                            move_line.amount_base, move_line.credit,
                            context=context)
                move_line_dt = {
                    'move_id': voucher_tax_sat.move_id.id,
                    'journal_id': voucher_tax_sat.journal_id.id,
                    'date': voucher_tax_sat.date,
                    'period_id': period_obj.find(cr, uid,
                                                    voucher_tax_sat.date,
                                                    context=context)[0],
                    'debit': move_line.credit,
                    'name': _('Close of IVA Retained'),
                    'partner_id' : move_line.partner_id.id,
                    'account_id': move_line.tax_id_secondary.account_id_creditable.id,
                    'credit': 0.0,
                    'amount_base': amount_base,
                    'tax_id_secondary': move_line.tax_id_secondary.tax_reference.id
                }
                move_line_cr = {
                    'move_id': voucher_tax_sat.move_id.id,
                    'journal_id': voucher_tax_sat.journal_id.id,
                    'date': voucher_tax_sat.date,
                    'period_id': period_obj.find(cr, uid,
                                                    voucher_tax_sat.date,
                                                    context=context)[0],
                    'debit': 0.0,
                    'name': _('Close of IVA Retained'),
                    'partner_id' : move_line.partner_id.id,
                    'account_id': move_line.tax_id_secondary.account_id_by_creditable.id,
                    'credit': move_line.credit,
                }
                for line_dt_cr in [move_line_dt, move_line_cr]:
                    aml_obj.create(cr, uid, line_dt_cr, context=context)
        return True
    
    def create_move_line_sat(self, cr, uid, voucher_tax_sat, amount, context=None):
        aml_obj = self.pool.get('account.move.line')
        period_obj = self.pool.get('account.period')
        vals = {
            'move_id': voucher_tax_sat.move_id.id,
            'journal_id': voucher_tax_sat.journal_id.id,
            'date': voucher_tax_sat.date,
            'period_id': period_obj.find(cr, uid,
                                                voucher_tax_sat.date,
                                                context=context)[0],
            'debit': 0,
            'name': _('Payment to SAT'),
            'partner_id': voucher_tax_sat.partner_id.id,
            'account_id': voucher_tax_sat.partner_id.property_account_payable.id,
            'credit': amount,
        }
        return aml_obj.create(cr, uid, vals, context=context)
    
    def create_move_sat(self, cr, uid, ids, context=None):
        account_move_obj = self.pool.get('account.move')
        context = context or {}
        ids= isinstance(ids,(int,long)) and [ids] or ids
        for move_tax_sat in self.browse(cr, uid, ids, context=context):
            vals_move_tax= account_move_obj.account_move_prepare(cr, uid,
                    move_tax_sat.journal_id.id,
                    date = move_tax_sat.date,
                    ref='Entry SAT', context=context)
        return account_move_obj.create(cr, uid, vals_move_tax, context=context)


    def sat_pay(self, cr, uid, ids, context=None):
        """
        """
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        if not ids: return []
        dummy, view_id = self.pool.get('ir.model.data').\
                                get_object_reference(cr, uid,
                                'account_voucher', 'view_vendor_payment_form')
        exp_brw = self.browse(cr, uid, ids[0], context=context)
        return {
            'name':_("Pay SAT"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'account.voucher',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'domain': '[]',
            'context': {
                'default_partner_id': exp_brw.partner_id.id,
                'default_amount': 0.0,
                'close_after_process': True,
                'default_type': 'payment',
                'type': 'payment',
            }
        }


class account_tax(osv.Model):
    
    _inherit = 'account.tax'
    
    _columns = {
        'tax_sat_ok': fields.boolean('Create entries IVA to SAT'),
        'account_id_creditable': fields.many2one('account.account',
                                        'Account of entries SAT Acreditable'),
        'account_id_by_creditable': fields.many2one('account.account',
                                        'Account of entries SAT x Acreditable'),
        'tax_reference': fields.many2one('account.tax',
            'Tax Reference',
            help = 'Tax Reference to get data of DIOT/SAT')
    }