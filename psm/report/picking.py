# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
from openerp.report import report_sxw
import pooler


class spm_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        if context is None:
            context = {}
        super(spm_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_psm': self.get_psm,
        })

    def get_psm(self, pickings):
        pool = pooler.get_pool(self.cr.dbname)
        products = []
        res = []
        aux = []
        for picking in pickings:
            ml_ids = picking.move_lines

            for ml_id in ml_ids:
                products.append(ml_id.product_id)
                products = list(set(products))

            for product in products:

                aux = self._get_serial(picking, product)
                if aux:

                    val = {
                        'product': pool.get('product.product').browse(self.cr, self.uid, [product.id])[0].name,
                        'nro_prod': len(aux),
                        'serial': ' | '.join(aux)
                    }
                    if val:
                            res.append(val)
                            val = {}
            return res

    def _get_serial(self, picking, product):
        res = []
        ml_ids = picking.move_lines
        for ml_id in ml_ids:
            if ml_id.product_id == product:
                if ml_id.prodlot_id.name:
                    res.append(ml_id.prodlot_id.name)
        return res


report_sxw.report_sxw('report.spm_report',
                      'stock.picking',
                      'addons/psm/report/picking.rml',
                      parser=spm_report)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
