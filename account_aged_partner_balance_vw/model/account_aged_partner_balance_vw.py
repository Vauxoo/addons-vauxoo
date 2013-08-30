# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: moylop260 (moylop260@vauxoo.com)
############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv
import openerp.tools as tools
from openerp.tools.translate import _

import openerp.netsvc as netsvc
import time
import os


class account_aged_partner_balance_vw(osv.Model):
    _name = 'account.aged.partner.balance.vw'
    _rec_name = 'partner_id'
    _auto = False
    _order = 'partner_id'

    _columns = {
        'partner_id': fields.many2one('res.partner', u'Partner'),
        'total': fields.float(u'Total'),
        'not_due': fields.float(u'Not Due'),
        'days_due_01to30': fields.float(u'01/30'),
        'days_due_31to60': fields.float(u'31/60'),
        'days_due_61to90': fields.float(u'61/90'),
        'days_due_91to120': fields.float(u'91/120'),
        'days_due_121togr': fields.float(u'+121'),
        #'pending': fields.float(u'Pending'),
        'company_id': fields.many2one('res.company', u'Company'),
        'currency_company_id': fields.many2one('res.currency', u'Company Currency'),
        #'currency_src_id': fields.many2one('res.currency', u'Source Currency'),
    }

    def init(self, cr):
        # FALTA AGREGAR INNER JOIN CON COMPANY, PARA CASAR LA MONEDA POR
        # DEFAULT Y TRANSFORMAR TODO A LA MONEDA DE LA COMPANY.
        move_obj = self.pool.get('account.move.line')
        ctx = {}
        # ACCOUNT_TYPE = ['receivable']#customer
        # ACCOUNT_TYPE = ['payable']#supplier
        # ACCOUNT_TYPE = ['payable','receivable']#supplier & customer
        # MOVE_STATE = ['posted']#, 'draft']
        move_query = move_obj._query_get(cr, 1, obj='l', context=ctx)
        # print 'en aged partner balance nueva modificacion---------------------------------------'
        # query en version 97 con errores
        #~ full_query ='''SELECT *
        #~ FROM (
            #~ SELECT MIN(l.id) as id, l.partner_id,
                #~ SUM(l.debit-l.credit) AS "total",
                #~ SUM(CASE WHEN              days_due <= 00 THEN l.debit-l.credit ELSE 0 END ) AS "not_due",
                #~ SUM(CASE WHEN days_due BETWEEN 01 AND  30 THEN l.debit-l.credit ELSE 0 END ) AS "days_due_01to30",
                #~ SUM(CASE WHEN days_due BETWEEN 31 AND  60 THEN l.debit-l.credit ELSE 0 END ) AS "days_due_31to60",
                #~ SUM(CASE WHEN days_due BETWEEN 61 AND  90 THEN l.debit-l.credit ELSE 0 END ) AS "days_due_61to90",
                #~ SUM(CASE WHEN days_due BETWEEN 91 AND 120 THEN l.debit-l.credit ELSE 0 END ) AS "days_due_91to120",
                #~ SUM(CASE WHEN days_due >=121              THEN l.debit-l.credit ELSE 0 END ) AS "days_due_121togr",
                #~ COALESCE( l.currency_id, res_company.currency_id) AS "currency_src_id",
                #~ res_company.currency_id AS "currency_company_id",
                #~ l.company_id,l.currency_id as lcurrency
            #~ FROM account_move_line l
            #~ INNER JOIN
               #~ (
                   #~ SELECT id, EXTRACT(DAY FROM (now() - COALESCE(lt.date_maturity,lt.date))) AS days_due
                   #~ FROM account_move_line lt
                   #~ --WHERE --lt.state, si ya finalizo no tiene fecha de vencimiento
               #~ ) l2
               #~ ON l2.id = l.id
            #~ INNER JOIN account_account
               #~ ON account_account.id = l.account_id
            #~ INNER JOIN res_company
               #~ ON account_account.company_id = res_company.id
            #~ INNER JOIN account_move
              #~ ON account_move.id = l.move_id
            #~ WHERE account_account.active
              #~ AND (account_account.type IN ('receivable'))
              #~ --AND (l.reconcile_id IS NULL)
              #~ AND account_move.state = 'posted'
              #~ --AND %s
            #~ --GROUP BY l.partner_id, l.currency_id, l.company_id, res_company.currency_id,l.currency_id --original
            #~ GROUP BY l.partner_id, COALESCE(l.currency_id, res_company.currency_id), l.company_id, res_company.currency_id
        #~ ) vw
        #~ WHERE  total <> 0
        #~ and lcurrency is null '''%(move_query)

    # modificado el 07/07/2011 Isaac

        full_query = '''select * from (
            SELECT MIN(l.id) as id, l.partner_id,
                SUM(l.debit-l.credit) AS "total",
                SUM(CASE WHEN              days_due <= 00 THEN l.debit-l.credit ELSE 0 END ) AS "not_due",
                SUM(CASE WHEN days_due BETWEEN 01 AND  30 THEN l.debit-l.credit ELSE 0 END ) AS "days_due_01to30",
                SUM(CASE WHEN days_due BETWEEN 31 AND  60 THEN l.debit-l.credit ELSE 0 END ) AS "days_due_31to60",
                SUM(CASE WHEN days_due BETWEEN 61 AND  90 THEN l.debit-l.credit ELSE 0 END ) AS "days_due_61to90",
                SUM(CASE WHEN days_due BETWEEN 91 AND 120 THEN l.debit-l.credit ELSE 0 END ) AS "days_due_91to120",
                SUM(CASE WHEN days_due >=121              THEN l.debit-l.credit ELSE 0 END ) AS "days_due_121togr",
                --COALESCE( l.currency_id, res_company.currency_id) AS "currency_src_id",
                --res_company.currency_id AS "currency_src_id",
                res_company.currency_id AS "currency_company_id",
                l.company_id
            FROM account_move_line l
            INNER JOIN
               (--Subquery add days_due to account_move_line
                   SELECT id, EXTRACT(DAY FROM (now() - COALESCE(lt.date_maturity,lt.date))) AS days_due
                   FROM account_move_line lt
                   --WHERE --lt.state, si ya finalizo no tiene fecha de vencimiento
               ) l2
               ON l2.id = l.id

            INNER JOIN account_account
               ON account_account.id = l.account_id
            INNER JOIN res_company
               ON account_account.company_id = res_company.id
            INNER JOIN account_move
               ON account_move.id = l.move_id
            WHERE account_account.active
                  AND (account_account.type IN ('receivable'))
                  AND (l.reconcile_id IS NULL)
                  AND account_move.state = 'posted'
            GROUP BY l.partner_id, l.company_id, res_company.currency_id--, l.currency_id
        ) vw
        WHERE  total <> 0'''

        tools.drop_view_if_exists(cr, '%s' % (self._name.replace('.', '_')))
        cr.execute("""CREATE OR REPLACE VIEW %s AS (
                %s
            )""" % ( self._name.replace('.', '_'), full_query ) )
account_aged_partner_balance_vw()
