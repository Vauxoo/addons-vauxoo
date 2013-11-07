# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Luis Torres (luis_t@vauxoo.com)
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
from openerp.tools.translate import _
from openerp.osv import fields, osv


class cif_config(osv.TransientModel):
    _name = 'cif.config'
    _inherit = 'res.config'

    def _write_company(self, cr, uid, cif_file, company_id, context=None):
        self.pool.get('res.company').write(cr, uid, company_id, {
            'cif_file': cif_file,
        }, context=context)

    def execute(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return True
        ids = isinstance(ids, (int, long)) and [ids] or ids
        company_id = self.pool.get('res.users').browse(
            cr, uid, [uid], context)[0].company_id.partner_id.id
        wiz_data = self.read(cr, uid, ids)
        if wiz_data[0]['cif_file']:
            self._write_company(cr, uid, wiz_data[0]["cif_file"], company_id, context)

    _columns = {
        'cif_file': fields.binary('CIF', help="Fiscal Identification Card"),
    }
