#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Juan Carlos Funes(juan@vauxoo.com)
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
import pooler
from report import report_sxw

class reportes_btree_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(reportes_btree_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'get_account_moves': self.get_account_moves,
            'get_account_min_level': self.get_account_min_level,

        })
    def get_account_min_level(self,form):
        account_ids = form and form[0]['account_ids'] or False
        nivel = form and form[0]['nivel']
        if account_ids:
            where_account_ids='parent.id in (%s)'%','.join(map(str,account_ids))
        else:
            where_account_ids='parent.id is not null'
        self.cr.execute(""" SELECT min(level)
                FROM(SELECT
                    node.id,node.name,node.code,
                    CAST ((count(parent.name)) AS INT) as level
                    FROM account_account AS node,account_account AS parent
                    where node.parent_left BETWEEN parent.parent_left AND parent.parent_right
                    GROUP BY node.name,node.parent_left,node.id , node.code
                    ORDER BY node.parent_left) nivel
                INNER JOIN
                (SELECT nivel.id,nivel.name,nivel.type
                FROM( SELECT
                    node.id as id,node.name,node.type
                    FROM account_account AS node,account_account AS parent
                    WHERE node.parent_left BETWEEN parent.parent_left AND parent.parent_right
                    AND """+where_account_ids+"""
                    ORDER BY parent.parent_left ) nivel
                    ) padres ON padres.id=nivel.id
                WHERE nivel.level<=%s """,
                (nivel,))
        dat=self.cr.dictfetchall()
        res= dat and dat[0]['min'] or False
        return res

    def get_account_moves(self, form):
        debit=0.0
        credit=0.0
        saldo_inicial=0.0
        saldo_final=0.0
        account_ids = form and form[0]['account_ids'] or False
        date_ini = form and form[0]['date_ini'] or False
        date_fin = form and form[0]['date_fin'] or False
        nivel = form and form[0]['nivel']
        partner = form and form[0]['partner']
        if account_ids:
            where_account_ids='parent.id in (%s)'%','.join(map(str,account_ids))
        else:
            where_account_ids='parent.id is not null'
        if partner==True:
            self.cr.execute("""SELECT subvw_final.partner,subvw_final.type,subvw_final.level,subvw_final.code,subvw_final.name,COALESCE(subvw_final.saldo_inicial,0.0::numeric) as saldo_inicial,subvw_final.debit,subvw_final.credit,
                COALESCE((subvw_final.debit-subvw_final.credit)+subvw_final.saldo_inicial,0.0::numeric) AS saldo_final
                FROM (
                    SELECT *, debit-credit AS balance
                            FROM (
                            SELECT account_child_and_consolidated.parent_id AS id,
                             COALESCE(SUM(l.credit), 0) AS credit,
                             COALESCE(SUM(l.debit), 0) AS debit
                             ,res_partner.name as partner
                               FROM (
                                SELECT account_child_vw.parent_id, COALESCE( account_consolidated_vw.child_id, account_child_vw.child_id) AS child_id,
                                 COALESCE( account_consolidated_vw.parent_currency_id, account_child_vw.parent_currency_id) AS parent_currency_id
                                FROM (
                                SELECT aa_tree_1.id AS parent_id, aa_tree_2.id AS child_id, aa_tree_1.currency_id AS parent_currency_id
                                FROM account_account aa_tree_1
                                LEFT OUTER JOIN account_account aa_tree_2
                                   ON aa_tree_2.parent_left
                                      BETWEEN aa_tree_1.parent_left AND aa_tree_1.parent_right
                                ) account_child_vw
                                LEFT OUTER JOIN
                                (
                                SELECT aa_tree_1.id AS parent_id, aa_tree_4.id AS child_id, aa_tree_1.currency_id AS parent_currency_id
                                FROM account_account_consol_rel
                                INNER JOIN account_account aa_tree_1
                                   ON aa_tree_1.id = account_account_consol_rel.child_id
                                INNER JOIN account_account aa_tree_2
                                   ON aa_tree_2.id = account_account_consol_rel.parent_id
                                LEFT OUTER JOIN account_account aa_tree_3
                                   ON aa_tree_3.parent_left
                                      BETWEEN aa_tree_1.parent_left AND aa_tree_1.parent_right
                                LEFT OUTER JOIN account_account aa_tree_4
                                   ON aa_tree_4.parent_left
                                      BETWEEN aa_tree_2.parent_left AND aa_tree_2.parent_right
                                ) account_consolidated_vw
                                ON account_child_vw.child_id = account_consolidated_vw.parent_id
                            ) account_child_and_consolidated
                            LEFT OUTER JOIN account_move_line l
                              ON l.account_id = account_child_and_consolidated.child_id join account_move
                              on l.move_id=account_move.id
                              join res_partner ON res_partner.id = l.partner_id
                            WHERE  account_move.state='posted' AND l.date >= %s AND l.date <= %s
                             GROUP BY account_child_and_consolidated.parent_id,res_partner.name) subvw
            JOIN
                (
        SELECT DISTINCT nivel.id,nivel.name,nivel.level,nivel.code,padres.type
            FROM(SELECT
                node.id,node.name,node.code,
                CAST ((count(parent.name)) AS INT) as level
                FROM account_account AS node,account_account AS parent
                where node.parent_left BETWEEN parent.parent_left AND parent.parent_right
                GROUP BY node.name,node.parent_left,node.id , node.code
                ORDER BY node.parent_left) nivel
            INNER JOIN
            (SELECT nivel.id,nivel.name,nivel.type
            FROM( SELECT
                node.id as id,node.name,node.type
                FROM account_account AS node,account_account AS parent
                WHERE node.parent_left BETWEEN parent.parent_left AND parent.parent_right
                AND """+where_account_ids+"""
                ORDER BY parent.parent_left ) nivel
                ) padres ON padres.id=nivel.id
            WHERE nivel.level<=%s
            ORDER BY nivel.code) subvw_level
        ON subvw_level.id = subvw.id
            LEFT JOIN
                (
                SELECT subvw.id as id_inicial,COALESCE((subvw.debit - subvw.credit),0.0::numeric) AS saldo_inicial
                   FROM ( SELECT account_child_and_consolidated.parent_id AS id, COALESCE(sum(l.credit), 0::numeric) AS credit,
                    COALESCE(sum(l.debit), 0::numeric) AS debit
                       FROM ( SELECT account_child_vw.parent_id, COALESCE(account_consolidated_vw.child_id, account_child_vw.child_id) AS child_id,
                        COALESCE(account_consolidated_vw.parent_currency_id, account_child_vw.parent_currency_id) AS parent_currency_id
                           FROM ( SELECT aa_tree_1.id AS parent_id, aa_tree_2.id AS child_id, aa_tree_1.currency_id AS parent_currency_id
                               FROM account_account aa_tree_1
                              LEFT JOIN account_account aa_tree_2 ON aa_tree_2.parent_left >= aa_tree_1.parent_left AND aa_tree_2.parent_left <= aa_tree_1.parent_right) account_child_vw
                          LEFT JOIN ( SELECT aa_tree_1.id AS parent_id, aa_tree_4.id AS child_id, aa_tree_1.currency_id AS parent_currency_id
                               FROM account_account_consol_rel
                              JOIN account_account aa_tree_1 ON aa_tree_1.id = account_account_consol_rel.child_id
                         JOIN account_account aa_tree_2 ON aa_tree_2.id = account_account_consol_rel.parent_id
                        LEFT JOIN account_account aa_tree_3 ON aa_tree_3.parent_left >= aa_tree_1.parent_left AND aa_tree_3.parent_left <= aa_tree_1.parent_right
                       LEFT JOIN account_account aa_tree_4 ON aa_tree_4.parent_left >= aa_tree_2.parent_left AND aa_tree_4.parent_left <= aa_tree_2.parent_right) account_consolidated_vw
                    ON account_child_vw.child_id = account_consolidated_vw.parent_id) account_child_and_consolidated
                      LEFT JOIN account_move_line l ON l.account_id = account_child_and_consolidated.child_id
                   JOIN account_move ON account_move.id = l.move_id
                  WHERE (l.state::text <> ALL (ARRAY['cancel'::character varying, 'draft'::character varying]::text[]))
                  AND account_move.state::text = 'posted'::text AND l.date < %s::date
                  GROUP BY account_child_and_consolidated.parent_id) subvw)subvw_inicial
                  ON subvw_level.id = subvw_inicial.id_inicial)subvw_final
                  ORDER BY subvw_final.code""",(date_ini, date_fin, nivel, date_ini,))
        else:
            self.cr.execute("""SELECT
            subvw_final.type,subvw_final.level,subvw_final.code,subvw_final.name,COALESCE(subvw_final.saldo_inicial,0.0::numeric) as saldo_inicial,subvw_final.debit,subvw_final.credit,
                COALESCE((subvw_final.debit-subvw_final.credit)+subvw_final.saldo_inicial,0) AS saldo_final
                FROM (
                    SELECT *, debit-credit AS balance
                            FROM (
                            SELECT account_child_and_consolidated.parent_id AS id,
                             COALESCE(SUM(l.credit), 0) AS credit,
                             COALESCE(SUM(l.debit), 0) AS debit
                               FROM (
                                SELECT account_child_vw.parent_id, COALESCE( account_consolidated_vw.child_id, account_child_vw.child_id) AS child_id,
                                 COALESCE( account_consolidated_vw.parent_currency_id, account_child_vw.parent_currency_id) AS parent_currency_id
                                FROM (
                                SELECT aa_tree_1.id AS parent_id, aa_tree_2.id AS child_id, aa_tree_1.currency_id AS parent_currency_id
                                FROM account_account aa_tree_1
                                LEFT OUTER JOIN account_account aa_tree_2
                                   ON aa_tree_2.parent_left
                                      BETWEEN aa_tree_1.parent_left AND aa_tree_1.parent_right
                                ) account_child_vw
                                LEFT OUTER JOIN
                                (
                                SELECT aa_tree_1.id AS parent_id, aa_tree_4.id AS child_id, aa_tree_1.currency_id AS parent_currency_id
                                FROM account_account_consol_rel
                                INNER JOIN account_account aa_tree_1
                                   ON aa_tree_1.id = account_account_consol_rel.child_id
                                INNER JOIN account_account aa_tree_2
                                   ON aa_tree_2.id = account_account_consol_rel.parent_id
                                LEFT OUTER JOIN account_account aa_tree_3
                                   ON aa_tree_3.parent_left
                                      BETWEEN aa_tree_1.parent_left AND aa_tree_1.parent_right
                                LEFT OUTER JOIN account_account aa_tree_4
                                   ON aa_tree_4.parent_left
                                      BETWEEN aa_tree_2.parent_left AND aa_tree_2.parent_right
                                ) account_consolidated_vw
                                ON account_child_vw.child_id = account_consolidated_vw.parent_id
                            ) account_child_and_consolidated
                            LEFT OUTER JOIN account_move_line l
                              ON l.account_id = account_child_and_consolidated.child_id join account_move
                              on l.move_id=account_move.id
                            WHERE  account_move.state='posted' AND l.date >= %s AND l.date <= %s
                             GROUP BY account_child_and_consolidated.parent_id ) subvw
            JOIN
                (
        SELECT DISTINCT nivel.id,nivel.name,nivel.level,nivel.code,padres.type
            FROM(SELECT
                node.id,node.name,node.code,
                CAST ((count(parent.name)) AS INT) as level
                FROM account_account AS node,account_account AS parent
                where node.parent_left BETWEEN parent.parent_left AND parent.parent_right
                GROUP BY node.name,node.parent_left,node.id , node.code
                ORDER BY node.parent_left) nivel
            INNER JOIN
            (SELECT nivel.id,nivel.name,nivel.type
            FROM( SELECT
                node.id as id,node.name,node.type
                FROM account_account AS node,account_account AS parent
                WHERE node.parent_left BETWEEN parent.parent_left AND parent.parent_right
                AND """+where_account_ids+"""
                ORDER BY parent.parent_left ) nivel
                ) padres ON padres.id=nivel.id
            WHERE nivel.level<=%s
            ORDER BY nivel.code) subvw_level
        ON subvw_level.id = subvw.id
           LEFT JOIN
                (
                SELECT subvw.id as id_inicial,COALESCE((subvw.debit - subvw.credit),0.0::numeric) AS saldo_inicial
                   FROM ( SELECT account_child_and_consolidated.parent_id AS id, COALESCE(sum(l.credit), 0::numeric) AS credit,
                    COALESCE(sum(l.debit), 0::numeric) AS debit
                       FROM ( SELECT account_child_vw.parent_id, COALESCE(account_consolidated_vw.child_id, account_child_vw.child_id) AS child_id,
                        COALESCE(account_consolidated_vw.parent_currency_id, account_child_vw.parent_currency_id) AS parent_currency_id
                           FROM ( SELECT aa_tree_1.id AS parent_id, aa_tree_2.id AS child_id, aa_tree_1.currency_id AS parent_currency_id
                               FROM account_account aa_tree_1
                              LEFT JOIN account_account aa_tree_2 ON aa_tree_2.parent_left >= aa_tree_1.parent_left AND aa_tree_2.parent_left <= aa_tree_1.parent_right) account_child_vw
                          LEFT JOIN ( SELECT aa_tree_1.id AS parent_id, aa_tree_4.id AS child_id, aa_tree_1.currency_id AS parent_currency_id
                               FROM account_account_consol_rel
                              JOIN account_account aa_tree_1 ON aa_tree_1.id = account_account_consol_rel.child_id
                         JOIN account_account aa_tree_2 ON aa_tree_2.id = account_account_consol_rel.parent_id
                        LEFT JOIN account_account aa_tree_3 ON aa_tree_3.parent_left >= aa_tree_1.parent_left AND aa_tree_3.parent_left <= aa_tree_1.parent_right
                       LEFT JOIN account_account aa_tree_4 ON aa_tree_4.parent_left >= aa_tree_2.parent_left AND aa_tree_4.parent_left <= aa_tree_2.parent_right) account_consolidated_vw
                    ON account_child_vw.child_id = account_consolidated_vw.parent_id) account_child_and_consolidated
                      LEFT JOIN account_move_line l ON l.account_id = account_child_and_consolidated.child_id
                   JOIN account_move ON account_move.id = l.move_id
                  WHERE (l.state::text <> ALL (ARRAY['cancel'::character varying, 'draft'::character varying]::text[]))
                  AND account_move.state::text = 'posted'::text AND l.date < %s::date
                  GROUP BY account_child_and_consolidated.parent_id) subvw)subvw_inicial
                  ON subvw_level.id = subvw_inicial.id_inicial)subvw_final
                  ORDER BY subvw_final.code
                    """,(date_ini, date_fin, nivel, date_ini,))
        res=self.cr.dictfetchall()

        min_level=self.get_account_min_level(form)
        for lin in  res:
            if lin['level'] == min_level:
                credit+=lin['credit']
                debit+=lin['debit']
                saldo_inicial+=lin['saldo_inicial']
                saldo_final+=lin['saldo_final']
        amount={
            'credit' : credit,
            'debit'  : debit,
            'name'   : 'Total',
            'saldo_inicial' : saldo_inicial,
            'saldo_final' : saldo_final,
            'code' : '' }
        res.append(amount)
        return res
report_sxw.report_sxw('report.reportes.btree.report', 'account.move', '/account_report_partner/report/account_report_btree.rml', parser=reportes_btree_report, header=False)






