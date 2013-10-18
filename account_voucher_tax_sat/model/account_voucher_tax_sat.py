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
        'name': fields.char('Name', size=128, help='Name of This Document'),
        'partner_id': fields.many2one('res.partner', 'Partner',
                                        help='Partner of SAT'),
        'period_id': fields.many2one('account.period', 'Period',
                                        help='Period of Entries to find'),
        'aml_ids': fields.many2many('account.move.line', 'voucher_tax_sat_rel',
                                        'voucher_tax_sat_id', 'move_line_id',
                                        'Move Lines', help='Entries to close'),
        'journal_id':fields.many2one('account.journal', 'Journal',
                                        help='Accounting Journal where Entries will be posted'), 
        'move_id': fields.many2one('account.move', 'Journal Entry',
                                        help='Accounting Entry'),
        'company_id':fields.many2one('res.company', 'Company', help='Company'), 

    }
    
    _defaults = {
        'company_id': lambda s, c, u, cx: s.pool.get('res.users').browse(c, u,
            u, cx).company_id.id,    
    }
    
    def action_close_tax(self, cr, uid, ids, context=None):
        aml_obj = self.pool.get('account.move.line')
        context = context or {}
        ids= isinstance(ids,(int,long)) and [ids] or ids
        for voucher_tax_sat in self.browse(cr, uid, ids, context=context):
            
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
                        'period_id': voucher_tax_sat.period_id.id,
                        'journal_id': voucher_tax_sat.journal_id.id,
                        'credit': 0.0,
                        'debit': move_line_tax.credit,
                        'amount_base': None,
                        'tax_id_secondary': None
                    }) for move_line_tax in voucher_tax_sat.aml_ids ]
                    
                cr.execute('UPDATE account_move_line '\
                            'SET amount_tax_unround = null '\
                            'WHERE id in %s ',(tuple(move_line_copy), ))
                            
        return True
    def create_entries_tax_iva_sat(self, cr, uid, voucher_tax_sat,
                                                            context=None):
        aml_obj = self.pool.get('account.move.line')
        av_obj = self.pool.get('account.voucher') 
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
                    'date': fields.datetime.now(),
                    'period_id': voucher_tax_sat.period_id.id,
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
                    'date': fields.datetime.now(),
                    'period_id': voucher_tax_sat.period_id.id,
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
        print voucher_tax_sat,'voucher_tax_sat'
        aml_obj = self.pool.get('account.move.line')
        vals = {
            'move_id': voucher_tax_sat.move_id.id,
            'journal_id': voucher_tax_sat.journal_id.id,
            'date': fields.datetime.now(),
            'period_id': voucher_tax_sat.period_id.id,
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