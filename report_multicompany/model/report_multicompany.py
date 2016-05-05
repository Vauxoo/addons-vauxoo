# coding: utf-8
#
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#
#    Coded by: Jorge Angel Naranjo (jorge_nr@vauxoo.com)
#
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
from openerp.osv import osv, fields


class ReportMulticompany(osv.Model):

    _name = 'report.multicompany'
    _order = 'sequence, id desc'

    _columns = {
        'company_id': fields.many2one('res.company', 'Company',),
        'report_id': fields.many2one('ir.actions.report.xml', 'Report Template', required=True,
                                     help="""This report template will be assigned for electronic invoicing in your company"""),
        'report_name': fields.related('report_id', 'report_name', type='char', string='Report Name', readonly=True),
        'sequence': fields.integer('Sequence'),
        'model': fields.many2one('ir.model', 'Model', required=True),
    }

    def _default_company(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        return user.company_id.id

    _defaults = {
        'company_id': _default_company,
        'sequence': 10,
    }

    #_sql_constraints = [
    #    ('report_company_uniq', 'unique (company_id, report_id, model)',
    #     'The combination of Report Template, Company and Model must be unique !'),
    #]

    def onchange_report_model(self, cr, uid, ids, report_id=False, context=None):
        actions_obj = self.pool.get('ir.actions.report.xml')
        ir_model_obj = self.pool.get('ir.model')
        model_id = False
        if report_id:
            report_data = actions_obj.browse(cr, uid, report_id)
            model_ids = ir_model_obj.search(
                cr, uid, [('model', '=', report_data.model)])
            model_id = model_ids and model_ids[0] or False
        return {'value': {'model': model_id}}

    def report_multicompany_create(self, cr, uid, report_id, company_id=False, sequence=False, context=None):
        """This function adds or updates a record in a report associated
            with a company in which if the record exists and performs
            an upgrade assigning the sequence minimal and subtract one.
            If this record not exist are creates and
            assigns in the sequence sequence minimal and subtract one
        """
        if context is None:
            context = {}

        if sequence is False:
            sequence = 10
        actions_obj = self.pool.get('ir.actions.report.xml')
        ir_model_obj = self.pool.get('ir.model')
        model_id = False
        report_data = actions_obj.browse(cr, uid, report_id)
        sequence_min_id = self.search(
            cr, uid, [('model', '=', report_data.model), ('company_id', '=', company_id)], limit=1) or False
        if sequence_min_id:
            sequence_min = self.browse(
                cr, uid, sequence_min_id[0]).sequence - 10
        else:
            sequence_min = sequence

        record_id = self.search(cr, uid, [('model', '=', report_data.model),
                                          ('report_id', '=', report_id),
                                          ('company_id', '=', company_id)])
        if record_id:
            self.write(cr, uid, record_id, {'sequence': sequence_min})
        else:
            model_ids = ir_model_obj.search(
                cr, uid, [('model', '=', report_data.model)])
            model_id = model_ids and model_ids[0] or False

            data_create = {'company_id': company_id,
                           'report_id': report_id,
                           'report_name': report_data.report_name,
                           'sequence': sequence_min,
                           'model': model_id}
            self.create(cr, uid, data_create)
        return True
