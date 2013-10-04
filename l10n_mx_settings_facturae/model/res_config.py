# -*- coding: utf-8 -*-
#
#
#    OpenERP, Open Source Business Applications
#    Copyright (C) 2004-2012 OpenERP S.A. (<http://openerp.com>).
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
#

import time
import datetime
from dateutil.relativedelta import relativedelta
from operator import itemgetter
from os.path import join as opj

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from openerp.tools.translate import _
from openerp.osv import fields, osv
from openerp import tools
from openerp import SUPERUSER_ID


class facturae_config_settings(osv.osv_memory):
    _name = 'facturae.config.settings'
    _inherit = 'res.config.settings'

    _columns = {
        'company_id': fields.many2one('res.company', 'Company',),
        'module_l10n_mx_facturae': fields.boolean('Electronic Invoice CFD', help="""Install module for electronic invoice CFD"""),
        'module_l10n_mx_facturae_cbb': fields.boolean('Electronic Invoice CBB', help="""Install module for electronic invoice CBB"""),
        'module_l10n_mx_facturae_pac_sf': fields.boolean('Electronic Invoice CFDI', help="""Install module for electronic invoice CFDI"""),
        'email_tmp_id': fields.many2one('email.template', 'Email Template'),
        'temp_report_id': fields.many2one('ir.actions.report.xml', 'Report Template',),
        'mail_server_id': fields.many2one('ir.mail_server', 'Outgoing Mail Server',),
    }

    def open_parameters_pac(self, cr, uid, ids, context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Parameters Pac',
            'view_mode': 'tree,form',
            'res_model': 'params.pac',
        }

    def _default_company(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        return user.company_id.id

    _defaults = {
        'company_id': _default_company,
    }

    def get_default_email_tmp_id(self, cr, uid, fields, context=None):
        company_id = self.pool.get('res.users').browse(
            cr, uid, uid, context=context).company_id.id
        email_obj = self.pool.get('email.template')
        email_tmp_id = False
        dat = email_obj.search(
            cr, uid, [('model', 'like', 'account.invoice'), ('company_id', '=', company_id)])
        data = dat and dat[0] or False
        if data:
            email_tmp_id = email_obj.browse(cr, uid, data)
        else:
            try:
                email_tmp_id = self.pool.get('ir.model.data').get_object(cr,
                                                                         uid, 'l10n_mx_ir_attachment_facturae',
                                                                         'email_template_template_facturae_mx')
            except:
                pass
        return {'email_tmp_id': email_tmp_id and email_tmp_id.id or False,
                'mail_server_id': email_tmp_id and email_tmp_id.mail_server_id.id or False,
                'temp_report_id':  email_tmp_id and email_tmp_id.report_template.id or False, }

    def create(self, cr, uid, values, context=None):
        confg_id = super(facturae_config_settings, self).create(
            cr, uid, values, context)
        email_obj = self.pool.get('email.template')
        actions_obj = self.pool.get('ir.actions.report.xml')
        webkit_header_obj = self.pool.get('ir.header_webkit')
        report_data = actions_obj.browse(
            cr, SUPERUSER_ID, [values.get('temp_report_id')])
        confg_data = self.browse(cr, uid, confg_id, context=context)
        if report_data:
            webkit_header_obj.write(cr, SUPERUSER_ID, [report_data[0].webkit_header.id], {
                                    'company_id': confg_data.company_id.id}, context=context)
        email_obj.write(cr, uid, [confg_data.email_tmp_id.id], {
                        'company_id': confg_data.company_id.id,
                        'mail_server_id': confg_data.mail_server_id.id,
                        'report_template': values['temp_report_id']},
                        context=context)
        return confg_id

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
