# -*- encoding: utf-8 -*-
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


class report_multicompany(osv.Model):

    _name = 'report.multicompany'

    _columns = {
        'company_id': fields.many2one('res.company', 'Company',),
        'report_id': fields.many2one('ir.actions.report.xml', 'Report Template',
                                     help="""This report template will be assigned for electronic invoicing in your company"""),
        'report_name': fields.text('Report Name'),
        'sequence': fields.integer('Sequence'),
        'model': fields.many2one('ir.model', 'Model', required=True),
    }

    def _default_company(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        return user.company_id.id

    _defaults = {
        'company_id': _default_company,
    }

    _sql_constraints = [
        ('report_company_uniq', 'unique (company_id, report_id, model)',
         'The combination of Report Template, Company and Model must be unique !'),
    ]

    def onchange_report_model_name(self, cr, uid, ids, report_id=False, context=None):
        actions_obj = self.pool.get('ir.actions.report.xml')
        ir_model_obj = self.pool.get('ir.model')
        model_id = False
        report_name = False
        if report_id:
            report_data = actions_obj.browse(cr, uid, report_id)
            model_ids = ir_model_obj.search(
                cr, uid, [('model', '=', report_data.model)])
            model_id = model_ids and model_ids[0] or False
            report_name = report_data.report_name or False
        return {'value': {'report_name': report_name, 'model': model_id}}

    def report_multicompany_create(self, cr, uid, company_id, report_id, sequence=0, context=None):
        '''
            This function adds or updates a record in a report associated
            with a company in which if the record exists and performs 
            an upgrade assigning 0 in the sequence and all other reports a 
            sequence 10. If this record not exist are creates and 
            assigns in the sequence 0 and the others belonging to 
            the model and company  is assigns Sequence 10
        '''
        actions_obj = self.pool.get('ir.actions.report.xml')
        report_data = actions_obj.browse(cr, uid, report_id)
        record_ids = self.search(cr, uid, [('company_id', '=', company_id),
                                           ('model', '=', report_data.model)])
        ir_model_obj = self.pool.get('ir.model')
        model_id = False
        record_id = self.search(cr, uid, [('company_id', '=', company_id),
                               ('model', '=',
                                report_data.model),
            ('report_id', '=', report_id)])
        if record_ids:
            list_update = list(set(record_ids) - set(record_id))
            self.write(cr, uid, list_update, {'sequence': 10})

        if record_id:
            self.write(cr, uid, record_id, {'sequence': sequence})
        else:
            model_ids = ir_model_obj.search(
                cr, uid, [('model', '=', report_data.model)])
            model_id = model_ids and model_ids[0] or False
            data_create = {'company_id': company_id,
                           'report_id': report_id,
                           'report_name': report_data.report_name,
                           'sequence': sequence,
                           'model': model_id}
            self.create(cr, uid, data_create)
        return True

    def create(self, cr, uid, vals, context=None):
        '''
            This function updates records of all reports that equal 
            model and company to sequence 10 before the insert the 
            new record, the new record is assigns with sequence 0.
        '''
        record_ids = self.search(
            cr, uid, [('company_id', '=', vals.get('company_id')),
                      ('model', '=', vals.get('model'))])
        self.write(cr, uid, record_ids, {'sequence': 10})
        return super(report_multicompany, self).create(cr, uid, vals, context)
