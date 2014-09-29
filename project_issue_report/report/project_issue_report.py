# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: María Gabriela Quilarque <gabriela@openerp.com.ve>
#    Planified by: Nhomar Hernandez
#    Finance by: Helados Gilda, C.A. http://heladosgilda.com.ve
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


from report import report_sxw
import pooler


class Late_payments(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(Late_payments, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'message': self._message,
        })
        self.context = context

    def _message(self, obj, company):
        company_pool = pooler.get_pool(self.cr.dbname).get('res.company')
        message = company_pool.browse(self.cr, self.uid, company.id, {
                                      'lang': obj.lang}).overdue_msg
        return message

report_sxw.report_sxw('report.account.late.payments.l10n.ve', 'res.partner',
                      'addons/late_payments_report/report/late_payments.rml', parser=Late_payments)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
