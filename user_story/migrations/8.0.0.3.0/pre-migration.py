# coding: utf-8
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
# ##############Credits########################################################
#    Coded by: Vauxoo C.A. (Edgar Rivero)
#    Planified by: Nhomar Hernandez
#    Audited by: Vauxoo C.A.
###############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################


def add_sequence_ac(cr):
    """
    Adding the sequence to acceptability criteria
    """
    cr.execute("""SELECT id, accep_crit_id, sequence_ac
               FROM acceptability_criteria
               ORDER BY accep_crit_id, name, id;""")

    dict_ac = {}
    ite = 0
    cur = 0
    for ac in cr.dictfetchall():
        if cur != ac['accep_crit_id']:
            cur = ac['accep_crit_id']
            ite = 1
        dict_ac.update({ac['id']: ite})
        ite += 1

    cr.execute("""ALTER TABLE acceptability_criteria
               ADD COLUMN old_sequence INTEGER""")

    for key, value in dict_ac.iteritems():
        sql = """
         UPDATE acceptability_criteria
         SET old_sequence = acceptability_criteria.sequence_ac,
            sequence_ac = %s
         WHERE id = %s
        """
        cr.execute(sql, (value, key))


def migrate(cr, version):
    if not version:
        return
    add_sequence_ac(cr)
