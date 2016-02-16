# coding: utf-8
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C)2010-  OpenERP SA (<http://openerp.com>). All Rights Reserved
#    App Author: Vauxoo
#
#    Developed by Oscar Alcala
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields


class MailMessage(models.Model):
    _inherit = 'mail.message'

    def _comment_bought(self, cr, uid, ids, name, arg, context=None):
        res = {}.fromkeys(ids, False)
        sale_report_obj = self.pool.get('sale.report')
        mail_cache = self.browse(cr, uid, ids, context)[0]
        where = """

        WHERE l.product_id IS NOT NULL AND
                   t.id={res_id} AND s.partner_id={partner_id}

            """.format(res_id=mail_cache.res_id,
                       partner_id=mail_cache.author_id.id)
        execute = """
            {select}
            FROM ( {_from} )
            {where}
            {group}
            """.format(
            select=sale_report_obj._select(),
            _from=sale_report_obj._from(),
            where=where,
            group=sale_report_obj._group_by())
        cr.execute(execute)
        if cr.fetchall():
            res[ids[0]] = True
        return res

    comment_bought = fields.Boolean(compute=_comment_bought,
                                    string='Comment Bought',
                                    store=True)
