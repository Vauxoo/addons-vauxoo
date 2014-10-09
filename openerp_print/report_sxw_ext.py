#!/usr/bin/python
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

from openerp.report import report_sxw
from lxml import etree
import subprocess
import os
import cStringIO
import base64
import time

import openerp.netsvc as netsvc
import openerp.tools as tools
import openerp.netsvc as netsvc

logger = netsvc.Logger()


def checkBins(*bin):
    bins = list(bin)

    searchPaths = os.environ["PATH"].split(":")
    for path in searchPaths:
        for bin in bins:
            if os.path.exists(os.path.join(path, bin)):
                bins.remove(bin)
        if bins == []:
            return
    raise IOError("required binaries not %s found" % ", ".join(bins))

checkBins("lpr")

    #~ def search_model(self,cr,uid,model)
        #~ pool = pooler.get_pool(cr.dbname)
        #~ print_report_obj =pool.get('print.model.reports')
        #~ file_data =get_file(cr,uid,report_data)
        #~
        #~ for pt_re in ptre_obj.browse(cr,uid,[('report_id.id','=',report_xml_id)])
            #~ print 'ID PRINT REPORT', pt_re
            #~ if pt_re:
                #~ self.create_single_pdf(cr, uid, ids, data, report_xml, context)
            #~ else:


class Printer(object):
    def __init__(self, opts={}):
        """initializes the printer with options"""
        self.options = []
        self.setOptions(opts)

    def write(self, text):
        """prints a string"""
        stdin = subprocess.Popen(["lpr", " ".join(
            self.options)], stdin=subprocess.PIPE).stdin
        stdin.write(text)
        stdin.close()

    def write_print(self, file, print_report, args):
        if print_report.gs_use:
            p = subprocess.Popen(args, stdout=subprocess.PIPE)
            q = subprocess.Popen(["lpr", '-P', print_report.printer, " ".join(
                self.options)], stdin=p.stdout)
        else:
            subprocess.Popen(["lpr", '-P', print_report.printer, "/tmp/mi_archivo.pdf", " ".join(
                self.options), ], stdin=subprocess.PIPE)

    def setOption(self, key, value=None):
        if value is None:
            option = "-o %s" % key
        elif key[0] == '-':
            option = "%s %s" % (key, value)
        else:
            option = "-o %s=%s" % (key, value)
        self.options.append(option)

    def setOptions(self, opts):
        """sets printer options from a dictionary"""
        for (key, value) in opts.items():
            self.setOption(key, value)

    def reset(self):
        """puts the printer back in its default state"""
        self.options = []


def check_state(cr, uid, print_report, model, id_obj):
    pool = pooler.get_pool(cr.dbname)
    model_brw = pool.get(model).browse(cr, uid, id_obj, context=None)
    if model_brw.state in print_report.state.split(','):
        return True
    return False


def get_file(cr, uid, report_data):
    file_print = open('/tmp/mi_archivo.pdf', 'wb+')
    file_print.write(report_data)
    file_print.close
    return file_print


def get_lpr_options(cr, uid, print_report):

    printerOptions = {
        "cpi": print_report.lpr_option_id.cpi,
        "lpi": print_report.lpr_option_id.lpi,
        "media": print_report.lpr_option_id.media,
        "orientation-requested": print_report.lpr_option_id.orientation_requested,
    }
    if print_report.lpr_option_id.fit_to_page:
        printerOptions.update({"fit-to-page": None})
    args = []
    if print_report.gs_use and print_report.gs_option_id:
        args = [
            'gs',
            '-sDEVICE=%s' % print_report.gs_option_id.device,
            '-sOutputFile=-',
            '-q',
            '-dBATCH',
            '-dNOPAUSE',
            '/tmp/mi_archivo.pdf',
        ]
    p = Printer(printerOptions)
    return (p, args)


def printt_report(cr, uid, print_report, file_print):
    p, args = get_lpr_options(cr, uid, print_report)
    for i in range(print_report.num_copies):
        p.write_print(file_print, print_report, args)
    return True


def validate_report(cr, uid, print_report, report_data, id_obj):

    file_data = get_file(cr, uid, report_data)

    if not print_report.printer in [False, "none"]:
        if print_report.depend_state and check_state(cr, uid, print_report, print_report.model_id.model.model, id_obj) or not print_report.depend_state:
            printt_report(cr, uid, print_report, file_data)
            return True
    return False


class _format(report_sxw._format):
    pass


class _float_format(report_sxw._float_format):
    pass


class _int_format(report_sxw._int_format):
    pass


class _date_format(report_sxw._date_format):
    pass


class _dttime_format(report_sxw._dttime_format):
    pass


class browse_record_list(report_sxw.browse_record_list):
    pass


class rml_parse(report_sxw.rml_parse):
    pass


class report_sxw(report_sxw.report_sxw):

    # metodo sobreescribed al original, imprime el pdf en la impresora que se
    # selecciono en ir.actions.report.xml
    def create(self, cr, uid, ids, data, context=None):
        pool = pooler.get_pool(cr.dbname)
        company_obj = pool.get('res.company')

        ir_obj = pool.get('ir.actions.report.xml')
        report_xml_ids = ir_obj.search(cr, uid,
                                       [('report_name', '=', self.name[7:])], context=context)
        if report_xml_ids:
            report_xml = ir_obj.browse(
                cr, uid, report_xml_ids[0], context=context)
        else:
            title = ''
            rml = tools.file_open(self.tmpl, subdir=None).read()
            report_type = data.get('report_type', 'pdf')

            class a(object):
                def __init__(self, *args, **argv):
                    for key, arg in argv.items():
                        setattr(self, key, arg)
            report_xml = a(title=title, report_type=report_type,
                           report_rml_content=rml, name=title, attachment=False, header=self.header)
        report_type = report_xml.report_type

        result = self.validate_report(
            cr, uid, report_xml.id, data['id'], context)

        if result['allow']:
            context.update({'allow': True})
        else:
            logger.notifyChannel(
                "info", netsvc.LOG_INFO, "NO SE PERMITE REIMPRIMIR")

        if result['check_note_use']:
            context.update({'check_note_use': True})

        if report_type in ['sxw', 'odt']:
            fnct = self.create_source_odt
        elif report_type in ['pdf', 'raw', 'html']:
            fnct = self.create_source_pdf
        elif report_type == 'html2html':
            fnct = self.create_source_html2html
        else:
            raise 'Unknown Report Type'

        fnct_ret = fnct(cr, uid, ids, data, report_xml, context)

        if not fnct_ret:
            return (False, False)
        #~ Here should go the check which verifies whether this report must
        #~ be printed or not
        if context.get('allow', False):
            printer = validate_report(cr, uid, result[
                                      'brw'], fnct_ret[0], data['id'])
            if printer:
                self.create_ir_print(cr, uid, report_xml.id, data['id'])
        else:
            pass
        return fnct_ret

    def create_ir_print(self, cr, uid, report_xml_id, id_obj):
        pool = pooler.get_pool(cr.dbname)
        ir_print_obj = pool.get('ir.print')
        res = {
            'report_id': report_xml_id,
            'model_id': id_obj,
        }
        ir_print_id = ir_print_obj.create(cr, uid, res)

    def validate_report(self, cr, uid, report_xml_id, id_obj, context):
        pool = pooler.get_pool(cr.dbname)
        print_report_obj = pool.get('print.model.reports')
        report_id = print_report_obj.search(
            cr, uid, [('report_id', '=', report_xml_id)])
        if report_id:
            res = {}
            brw = print_report_obj.browse(cr, uid, report_id[0], context)
            res.update({'brw': brw})
            if brw.allow_repeat == False:
                res.update({'allow': print_report_obj.check_print(
                    cr, uid, brw.id, report_xml_id, id_obj, context)})
            else:
                res.update({'allow': True})
            res.update({'check_note_use': brw.check_note_use})
        return res

    def _default_company(self, cr, uid, context={}):
        pool = pooler.get_pool(cr.dbname)
        user = pool.get('res.users').browse(cr, uid, uid, context=context)
        company_obj = pool.get('res.company')
        company_id = company_obj.search(
            cr, uid, [('parent_id', '=', False)])[0]
        if company_obj:
            return company_obj.browse(cr, uid, user.company_id.id, context)

    def process_header(self, cr, uid, processed_rml, context):
        if context.get('check_note_use', False):
            pool = pooler.get_pool(cr.dbname)
            # banco = ir_objj.browse(cr, uid, data['context']['bank_id'] ,
            # context=None) #no funiona este con GTK
            banco = pool.get('res.bank').browse(
                cr, uid, context['bank_id'], context=None)
            self._add_header_bank(processed_rml, banco.format_h)
        elif not context.get('allow', False):
            header = self._default_company(cr, uid, context).header_report
            self._add_header_bank(processed_rml, header)

    # metodo que sobreescribe al original, en la impresion de la cabecara del
    # reporte
    def create_single_pdf(self, cr, uid, ids, data, report_xml, context=None):
        if not context:
            context = {}
        logo = None
        context = context.copy()
        title = report_xml.name
        rml = report_xml.report_rml_content
        if not rml:
            return False
        rml_parser = self.parser(cr, uid, self.name2, context=context)
        objs = self.getObjects(cr, uid, ids, context)
        rml_parser.set_context(objs, data, ids, report_xml.report_type)
        processed_rml = self.preprocess_rml(
            etree.XML(rml), report_xml.report_type)
        if report_xml.header:
            rml_parser._add_header(processed_rml, self.header)
        ################################
        self.process_header(cr, uid, processed_rml, context)
        ##################################
        if rml_parser.logo:
            logo = base64.decodestring(rml_parser.logo)
        create_doc = self.generators[report_xml.report_type]
        pdf = create_doc(etree.tostring(
            processed_rml), rml_parser.localcontext, logo, title.encode('utf8'))
        return (pdf, report_xml.report_type)

    # metodo que sobreescribe al original, agrega el cheque como cabecera en
    # el reporte
    def _add_header_bank(self, rml_dom, bank_header):
        head_dom = etree.XML(bank_header)
        for tag in head_dom:
            found = rml_dom.find('.//'+tag.tag)
            if found is not None and len(found):
                if tag.get('position'):
                    found.append(tag)
                else:
                    found.getparent().replace(found, tag)
        return True

    # metodo que sobreescribe al original, gestion de attachment
    def create_source_pdf(self, cr, uid, ids, data, report_xml, context=None):
        flag = False
        if not context:
            context = {}
        pool = pooler.get_pool(cr.dbname)
        attach = report_xml.attachment
        #~
        #~ Check in the new model if this report allow to reprint,
        #~ Allowtoreprint should mandate over attach,
        if attach:
            objs = self.getObjects(cr, uid, ids, context)
            results = []
            for obj in objs:
                aname = eval(attach, {'object': obj, 'time': time})
                result = False
                if report_xml.attachment_use and aname and context.get('attachment_use', True):
                    aids = pool.get('ir.attachment').search(cr, uid, [('datas_fname', '=', aname+'.pdf'), (
                        'res_model', '=', self.table), ('res_id', '=', obj.id)])
                    if aids:
                        brow_rec = pool.get(
                            'ir.attachment').browse(cr, uid, aids[0])
                        #~ if not brow_rec.datas:
                            #~ continue
                        #~ d = base64.decodestring(brow_rec.datas)
                        #~ results.append((d,'pdf'))
                        #~ continue
                result = self.create_single_pdf(cr, uid, [
                                                obj.id], data, report_xml, context)
                if not result:
                    return False
                try:
                    if aname:
                        flag = True  # ya que entra solo la primera vez sin attachment
                        name = aname+'.'+result[1]
                        pool.get('ir.attachment').create(cr, uid, {
                            'name': aname,
                            'datas': base64.encodestring(result[0]),
                            'datas_fname': name,
                            'res_model': self.table,
                            'res_id': obj.id,
                        }, context=context
                        )
                        cr.commit()

                except Exception, e:
                    import traceback
                    import sys
                    tb_s = reduce(lambda x, y: x+y, traceback.format_exception(
                        sys.exc_type, sys.exc_value, sys.exc_traceback))
                    netsvc.Logger().notifyChannel(
                        'report', netsvc.LOG_ERROR, str(e))
                results.append(result)
            if results:
                if results[0][1] == 'pdf':
                    if not context.get('allow', False):
                        return self.create_single_pdf(cr, uid, ids, data, report_xml, context)
                    else:
                        from pyPdf import PdfFileWriter, PdfFileReader
                        output = PdfFileWriter()
                        for r in results:
                            reader = PdfFileReader(cStringIO.StringIO(r[0]))
                            for page in range(reader.getNumPages()):
                                output.addPage(reader.getPage(page))
                        s = cStringIO.StringIO()
                        output.write(s)
                        return s.getvalue(), results[0][1]
        return self.create_single_pdf(cr, uid, ids, data, report_xml, context)
