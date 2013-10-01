# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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
import openerp.tools as tools
import os
from openerp.tools import assertion_report
import sys
import base64
from openerp.osv import osv, fields
import tempfile

class test_yaml_data_sale(osv.osv_memory):
    
    _name = 'test.yaml.data.sale'
    
    _columns = {
        'yaml_file': fields.binary('File sale order worng'),
        'yaml_file_log': fields.binary('File Log'),
        'filename_product': fields.char('File name', size=128, readonly=True),
        'filename_log_general': fields.char('File name log', size=128, readonly=True),
        'test_commit': fields.boolean('Commit')
    }
    
    _defaults={
        'test_commit' : False,
    }
    
    def test_sale (self, cr, uid, ids, context=None):
        assertion_obj = assertion_report.assertion_report()
        this = self.browse(cr, uid, ids)[0]
        fp_data = tools.file_open(os.path.join('sale_test_data_imp', 'test/sale_order_test_data.xml'))
        fp_test = tools.file_open(os.path.join('sale_test_data_imp', 'test/sale_order_product_can_be_sold.yml'))
        try:
            cr.execute("SAVEPOINT test_yaml_sale_savepoint")
            tools.convert_xml_import(cr, 'sale_test_data_imp', fp_data , {}, 'init', False, assertion_obj)
            tools.convert_yaml_import(cr, 'sale_test_data_imp', fp_test ,'test', {}, 'init', False, assertion_obj)
        finally:
            if this.test_commit:
                cr.execute("RELEASE SAVEPOINT test_yaml_sale_savepoint")
            else:
                cr.execute("ROLLBACK TO test_yaml_sale_savepoint")
                
        fp_data.close()
        fp_test.close()
        if tools.config['test_report_directory']:
            file_sale_order_wrong = base64.encodestring(open(os.path.join(tools.config['test_report_directory'],'sale_order_product_log.csv'), 'rb+').read())
            file_sale_order_log = base64.encodestring(open(os.path.join(tools.config['test_report_directory'],'sale_order_general_log.csv'), 'rb+').read())
        else:
            tmp_path = tempfile.gettempdir()
            file_sale_order_wrong = base64.encodestring(open(os.path.join(tmp_path,'sale_order_product_log.csv'), 'rb+').read())
            file_sale_order_log = base64.encodestring(open(os.path.join(tmp_path,'sale_order_general_log.csv'), 'rb+').read())
            
        self.write(cr, uid, ids, {
                        'yaml_file': file_sale_order_wrong,
                        'yaml_file_log' : file_sale_order_log,
                        'filename_product': 'sale_order_product_log.csv',
                        'filename_log_general' : 'sale_order_general_log.csv',
                        }, context=context)
                                
        __, xml_id = self.pool.get('ir.model.data').get_object_reference(
                cr, uid, 'sale_test_data_imp', 'view_wizard_sale_test_data_result')
                
        return {
                'res_model': 'test.yaml.data.sale',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': xml_id,
                'res_id': this.id,
                'context': context,
                'type': 'ir.actions.act_window',
                'target': 'new',
            }
