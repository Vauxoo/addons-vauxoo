# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: Maria Gabriela Quilarque  <gabrielaquilarque97@gmail.com>
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

from openerp.osv import fields, osv

import cupstree


class print_model(osv.Model):

    _name = 'print.model'
    _description = '''Class to introduce the model to send to the printer'''

    _columns = {
        'model': fields.many2one('ir.model', 'Modelo', required=True, help='Introduzca en este campo el modelo que sera enviado directamente a la impresora'),
        'model_report_ids': fields.one2many('print.model.reports', 'model_id', 'Modelo Reports', required=True,),
    }
    _rec_name = 'model'
    _sql_constraint = [(
        'name_uniq', 'unique(model)', 'No se puede repetir un modelo')]


class print_lpr_option(osv.Model):
    _name = 'print.lpr.option'
    _description = ''' http://www.cups.org/documentation.php/options.html '''

    _columns = {
        'name': fields.char('Name', size=256, required=True, help='Set the name for this LPR Profile'),
        'cpi': fields.integer('Number of Characters Per Inch', help='Sets the number of characters per inch'),
        'lpi': fields.integer('Number of Lines Per Inch', help='Sets the number of lines per inch'),
        'media': fields.selection([
            ('Letter', 'Letter'),
            ('Legal', 'Legal'),
            ('A4', 'A4'),
            ('DL', 'DL'),
            ('halfletter', 'Half Letter'),
        ], 'Media', help='Sets the media size'),
        'fit_to_page': fields.boolean('Fit to page', help='Specifies that the document should be scaled to fit on the page'),
        'orientation_requested': fields.selection([
            ('3', 'Portrait (no rotation)'),
            ('4', 'Landscape (90 degrees)'),
            ('5', 'Reverse landscape (270 degrees)'),
            ('6', 'Reverse portrait (180 degrees)'),
        ], 'Orientation Requested', help='The orientation-requested option rotates the page depending on the value of N:\n3 - portrait orientation (no rotation)\n4 - landscape orientation (90 degrees)\n5 - reverse landscape or seascape orientation (270 degrees)\n6 - reverse portrait or upside-down orientation (180 degrees)'),
    }


class print_gs_option(osv.Model):
    _name = 'print.gs.option'
    _description = ''' ftp://mirror.switch.ch/mirror/ghost/gs5man_e.pdf '''

    _columns = {
        'name': fields.char('Name', size=256, required=True, help='Set the name for this Ghostscript'),
        'device': fields.selection([
            ('epson', ' Epson-compatible dot matrix printer (9 or 24 pi'),
            ('eps9mid', 'Epson-compatible 9-pin, intermediate resolution'),
            ('eps9high', ' Epson-compatible 9-pin, triple resolutio'),
        ], 'Device Driver', help='Sets the device driver'),
    }


class print_model_reports(osv.Model):
    _name = 'print.model.reports'
    _description = '''Class used for introduce the report to print and this features.'''

    def _get_print(self, cr, uid, context={}):
        lista_p = []
        try:
            lista = cupstree.gethost()
            for i in lista:
                lista_p.append((i, i))
            lista_p.append(("none", 'None'))
        except:
            lista_p.append(("none", 'None'))
        return lista_p

    _columns = {
        'model_id': fields.many2one('print.model', string='Model', ondelete='cascade'),
        'num_copies': fields.integer('Number of Copies', help='Set the number of copies to print'),
        'report_id': fields.many2one('ir.actions.report.xml', 'Report', required=True, help='Set in this field, the model to send directing to the printer'),
        'lpr_option_id': fields.many2one('print.lpr.option', 'Lpr Options'),
        'gs_option_id': fields.many2one('print.gs.option', 'Ghostscript Options'),
        'printer': fields.selection(_get_print, size=256, string='Printers', help="Select the printer that will be used for print the report", select=True,),
        'allow_repeat': fields.boolean('Allow print again', help="Checking this field will allow you to print more than once this report",),
        'depend_state': fields.boolean('Depends State', help="Checking this field to allow the printing by states filter"),
        'check_note_use': fields.boolean('Use to print Check?', help="Checking this field when allow you to take different headers to print"),
        'state': fields.char('States', size=256, required=False, help='Set the states to used for allow the printing of the document. States must be separated by commas and no spaces. Example: draft,open,done. The state field must be defined in the model as state'),
        'gs_use': fields.boolean('Use Ghostscript?', help="Checking this field will allow to print Ghostscript options"),
        'python_code': fields.text('Python Code', size=1024, help='Set the python code to use',),
    }
    _rec_name = 'report_id'
    _defaults = {
        'printer': lambda *a: 'none',
        'num_copies': lambda *a: 1,
    }

    def check_print(self, cr, uid, id, report_xml_id, model_id, context={}):
        ir_print_obj = self.pool.get('ir.print')

        print_brw = self.browse(cr, uid, id, context=None)

        result_ids = ir_print_obj.search(cr, uid, [(
            'report_id', '=', report_xml_id), ('model_id', '=', model_id)])
        if result_ids and not print_brw.allow_repeat:
            return False
        return True


class ir_print(osv.Model):
    _name = 'ir.print'
    _description = ''' '''

    _columns = {
        'report_id': fields.many2one('ir.actions.report.xml', 'Report', readonly=True),
        'model_id': fields.integer('Document', readonly=True),
        'create_date': fields.datetime('Date Created', readonly=True),
        'create_uid': fields.many2one('res.users', 'Creator', readonly=True),
    }
