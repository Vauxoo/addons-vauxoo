# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
#
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
#
##############################################################################

from osv import osv
from osv import fields
import decimal_precision as dp
import netsvc
from tools.translate import _
#Excel Stuff
import xlrd
import xlwt
import base64
from tempfile import NamedTemporaryFile
from datetime import date, datetime, timedelta


class account_bank_statement(osv.osv):
    _inherit = 'account.bank.statement'

    def _fromto(self,cr,uid,ids,field,arg,context=None):
        statements=self.browse(cr,uid,ids,context=context)
        result={}
        for st in statements:
            result[st.id]=str(self._get_date_range(cr,uid,ids,context=context))
        return result

    _columns = {
        'bs_line_ids':fields.one2many('bank.statement.imported.lines', 'bank_statement_id', 'Statement', required=False),
        'fname':fields.char('File Name Imported',128,required=False),
        'from_to_file':fields.function(_fromto, string='Date Range on file', type='char'),
    }

    def file_verify_cr(self, cr, uid, ids, context={}):
        '''
        Verification of format Files.
        For CR Banco Nacional
        #Oficina	FechaMovimiento	NumDocumento	Debito	Credito	Descripcion
        '''
        sheet=context.get('xls_sheet')
        if sheet:
            if sheet.cell(0,0).value=='Oficina' and \
            sheet.cell(0,1).value=='FechaMovimiento' and \
            sheet.cell(0,2).value=='NumDocumento' and \
            sheet.cell(0,3).value=='Debito' and \
            sheet.cell(0,4).value=='Credito' and \
            sheet.cell(0,5).value=='Descripcion':
                return True
        return False

    def xlrd_to_date(self,cv):
        from1900to1970 = datetime(1970,1,1) - datetime(1900,1,1) + timedelta(days=2)
        print cv
        value = date.fromtimestamp( int(cv) * 86400) - from1900to1970
        print value
        return value

    def write_file(self, cr, uid, ids, context={}):
        sheet=context.get('xls_sheet')
        for i in range(sheet.nrows - 1):
            if i:
                l = {'office':int(sheet.cell_value(i,0)),
                'date':self.xlrd_to_date(sheet.cell_value(i,1)),
                'numdocument':sheet.cell_value(i,2),
                'debit':sheet.cell_value(i,3) and float(sheet.cell_value(i,3).replace(',','')),
                'credit':sheet.cell_value(i,4) and float(sheet.cell_value(i,4).replace(',','')),
                'name':sheet.cell_value(i,5),
                }
                
                self.write(cr,uid,ids,{'bs_line_ids':[(0,0,l)]}, context=context)
        return True

    def delete_lines_file(self, cr, uid, ids, context = None):
        bs=self.browse(cr,uid,ids,context=context)[0]
        bs.bs_line_ids and [self.write(cr, uid, ids, {'bs_line_ids':[(2,i.id)]}) for i in bs.bs_line_ids]
        self.write(cr, uid, ids, {'fname':''},context=context)
        return True

    def set_date_period(self, cr, uid, ids, context=None):
        p_obj=self.pool.get('account.period')
        st=self.browse(cr,uid,ids,context=context)[0]
        company_id=st.company_id.id
        range_dates = self._get_date_range(cr,uid,ids,context=context)
        ini_period=p_obj.find(cr,uid,range_dates[0],context={'company_id':company_id})
        end_period=p_obj.find(cr,uid,range_dates[1],context={'company_id':company_id})
        if ini_period <> end_period:
            raise osv.except_osv(_("Warning"),_("You can not make a bank reconcilation for bank moves with dates on different periods"))
        else:
            self.write(cr,uid,ids,{'period_id':ini_period[0],
                                   'date':range_dates[1]},context=context)
        return True

    def _get_date_range(self, cr, uid, ids, context=None):
        lines=self.browse(cr,uid,ids,context=context)[0].bs_line_ids
        dates=sorted([d.date for d in lines])
        date_range=dates and (dates[0],dates[-1]) or () 
        return date_range

    def create_aml_tmp(self, cr, uid, ids, context=None):
        am_obj=self.pool.get('account.move')
        aml_obj=self.pool.get('account.move.line')
        p_obj=self.pool.get('account.period')
        st=self.browse(cr,uid,ids,context=context)[0]
        company_id=st.company_id.id
        period_w=self.browse(cr,uid,ids,context=context)[0].period_id
        am_id=am_obj.create(cr, uid, {'name':'From File',
                                 'period_id':period_w.id,
                                 'journal_id':self.browse(cr,uid,ids,context=context)[0].journal_id.id,
                                 'date':self.browse(cr,uid,ids,context=context)[0].date,
                                 'narration':'''Account move created with importation from file %s
                                 ''' % (st.fname),
                                }, context=context)
        range_dates = self._get_date_range(cr,uid,ids,context=context)
        ini_period=p_obj.find(cr,uid,range_dates[0],context={'company_id':company_id})
        end_period=p_obj.find(cr,uid,range_dates[1],context={'company_id':company_id})
        if ini_period <> end_period:
            raise osv.except_osv(_("Warning"),_("You can not make a bank reconcilation for bank moves with dates on different periods"))

        if ini_period <> end_period <> [period_w.id]:
            raise osv.except_osv(_("Warning"),_("You can not make a bank reconcilation in a period different to the period indicated on files, please select correct period it should be %s " % (ini_period and ini_period[0])))
            

        for bsl in st.bs_line_ids:
            acc_id=bsl.debit and  st.journal_id.default_credit_account_id.id or st.journal_id.default_debit_account_id.id
            aml_obj.create(cr,uid,{'move_id':am_id,
                                   'name':bsl.name,
                                   'date':bsl.date,
                                   'credit':bsl.debit,
                                   'debit':bsl.credit,
                                   'stff_id':bsl.id,
                                   'account_id':acc_id,},
                                  context=context)
            aml_obj.create(cr,uid,{'move_id':am_id,
                                   'name':bsl.name,
                                   'date':bsl.date,
                                   'credit':bsl.credit,
                                   'debit':bsl.debit,
                                   'stff_id':bsl.id,
                                   'account_id':payrec_id,},

        self.log(cr, uid, st.id, _('Account Move Temporary For this Statement \
                                    Id Was Created is created %s ') % (st.id))
        am_obj.log(cr, uid, am_id, _('Account Move Temporary is created %s ') % (am_id))
        return True

    def read_file(self, cr, uid, ids, context=None):
        att_obj=self.pool.get('ir.attachment')
        file_xls_ids=att_obj.search(cr,uid,[('res_model','=','account.bank.statement'),('res_id','in',ids)])
        if len(file_xls_ids)<>1:
            raise osv.except_osv(_('Warning'), _('I found quatity of attachments <> 1 ! \
            Please Attach JUST One XLS file to this bank statement.'))
        file_xls_brw=att_obj.browse(cr, uid, file_xls_ids, context=context)
        if len(file_xls_ids)==1:
            checkfilename=file_xls_brw[0].datas_fname and file_xls_brw[0].datas_fname.endswith('.xls')
            if checkfilename:
                f=NamedTemporaryFile(delete=False)
                f.write(base64.b64decode(file_xls_brw[0].datas))
                print f.name
                doc=xlrd.open_workbook(f.name)
                print doc
                sheet = doc.sheet_by_index(0)
                context.update({'xls_sheet':sheet})
                if self.file_verify_cr(cr, uid, ids, context=context):
                    if self.write_file(cr, uid, ids, context=context):
                        self.write(cr, uid, ids, {'fname':file_xls_brw[0].datas_fname},context=context)
                        self.set_date_period(cr,uid,ids,context=context)
            else:
                raise osv.except_osv(_('Warning'), _('File Must be an XLS file ! \
                Please verify save as correctly in excel your exported file from bank statement'))
        file_xls_brw=att_obj.browse(cr,uid,file_xls_ids, context=context)
        return True

account_bank_statement()

class bank_statement_imported_lines(osv.osv):
    """
    OpenERP Model : ClassName
    """
    
    _name = 'bank.statement.imported.lines'
    _description = 'Imported lines for banks files'
    
    _columns = {
        'name':fields.char('Description', size=255, required=True, readonly=False),
        'date': fields.date('Date', required=True),
        'numdocument':fields.char('Num Document', size=64, required=True, readonly=False),
        'debit': fields.float('Debit', digits_compute=dp.get_precision('Account'), required=True),
        'credit': fields.float('Credit', digits_compute=dp.get_precision('Account'), required=True),
        'office':fields.char('Office', size=16, required=False, readonly=False),
        'bank_statement_id':fields.many2one('account.bank.statement', 'Bank Statement', required=True),
        'company_id':fields.many2one('res.company','Company',required=False),
        'aml_ids':fields.one2many('account.move.line', 'stff_id', 'Account Move Lines'),

    }

    _defaults = {
        'name': lambda *a: None,
        'company_id':  lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'account.account', context=c),
    }
bank_statement_imported_lines()

class account_move_line(osv.osv):

    _inherit='account.move.line'
    _columns = {
            'stff_id':fields.many2one('bank.statement.imported.lines','Statement from File line'),
            }
account_move_line()
