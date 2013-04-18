# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: Maria Gabriela Quilarque gabriela@openerp.com.ve
#              Luis Escobar luis@vauxoo.com
#    Planified by: Maria Gabriela Quilarque gabriela@openerp.com.ve
#    Finance by: Vauxoo, C.A. http://www.vauxoo.com
#    Audited by: Humberto Arocha humberto@openerp.com.ve
#############################################################################
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
##############################################################################

import time
from report import report_sxw


class move_voucher_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(move_voucher_report, self).__init__(
            cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_user_create': self._get_user_create,
        })

    def _get_user_create(self, move_id):
        info = self.cr.execute(
            "SELECT create_uid FROM account_move WHERE id = %s" % move_id)
        res = [x[0] for x in self.cr.fetchall()][0]

        user_obj = self.cr.execute(
            "SELECT name FROM res_users WHERE id = %s" % res)
        user_name = [x[0] for x in self.cr.fetchall()][0]
        return user_name

report_sxw.report_sxw(  # nuevo
    'report.account.move_vauxoo',
    'account.move',
    'addons/report_move_voucher/report/move_voucher.rml',
    parser=move_voucher_report,
    header=False
)
