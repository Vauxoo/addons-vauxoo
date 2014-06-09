# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2014 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Julio Serna(julio@vauxoo.com)
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
import time
import pooler
from report import report_sxw

class orden_dia(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(orden_dia, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_lines':self.get_lines,
        })

    def get_lines(self):
        query = """
                SELECT
                    CASE WHEN mol.type = 'correctivo' THEN 'Correctivo' ELSE 'Preventivo' END as tipo,
                    notes,
                    date,
                    date_release,
                    SUM(mml.product_qty*mml.costo) as costo,
                    mol.name as name,
                    pt.name as tracto
                FROM
                    maintenance_order_line mol
                LEFT JOIN
                    maintenance_material_line mml ON mol.id = mml.line_id
                JOIN
                    product_product pp ON mol.product_id = pp.id
                JOIN
                    product_template pt ON pp.product_tmpl_id = pt.id
                WHERE
                    mol.state IN ('draft')
                GROUP BY
                    mol.type, notes, date, date_release, mol.name, pt.name
                ORDER BY
                    pt.name, date"""
        self.cr.execute(query)
        res = self.cr.dictfetchall()
        return res

report_sxw.report_sxw('report.orden.dia', 'maintenance.order.line','addons/maintenance/report/account_tax_code.rml', parser=orden_dia, header=False)

