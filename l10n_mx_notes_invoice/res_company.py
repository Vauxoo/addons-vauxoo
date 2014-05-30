# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Luis Torres (luis_t@vauxoo.com)
#    Launchpad Project Manager for Publication: Nhomar Hernandez - nhomar@vauxoo.com
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

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import pooler, tools


class res_company(osv.Model):
    _inherit = 'res.company'

    _columns = {
        'dinamic_text' : fields.text('Promissory note', translate=True,
            help='This text will put in the report of model that you declared in this configuration'),
        'dict_var' : fields.text('Variables for text',
            help='Put te variables used in text'),
        'sample_text' : fields.text('Promissory note', readonly=True),
        'sample_dict' : fields.text('Variables to use in text', readonly=True),
        'details' : fields.text('Variables to use in text', readonly=True),
        'sample' : fields.text('Variables to use in text', readonly=True),
        'help': fields.boolean('Show Help', help='Allows you to show the help in the form'),
    }
    
    _defaults = {
        'details': _("The correct filling of these fields is as follow: \n In 'Promissory note' "\
            "put the text that you like show in the reports that call this notes, with the next "\
            "format: \n \t 'model': '''text''' \n \r Where: 'model' is the object where was"\
            "take the data for the notes and the 'text' is the text that you like show, in the "\
            "text you can add values of model, with the next code %(name_variable)s, and you "\
            "must declare name_variable in the field 'Variables to use in text' as follows: "\
            "'model': {'name_variable': iterations on model to reach the field to show}.\n"\
            "For more of and model you need set the next format:\n In Promissory note: "\
            "'model': '''text''', 'model': '''text''', \n In Variables to use in text: "\
            "'model: {'name_variable': iteration, 'variable2': iteration}|'model': "\
            "{'name_variable': iteration}, you can see that in Variables to use in text I was"\
            "separated the models with an '|'. \n NOTE: If you need use symbol '%', you need "\
            "use %%."),
        'sample': _("If you like put the text in Facturae Report \n'I MyPartner promissory "\
            "note to the order of My Company the amount of $500.00', and in the report of "\
            "Paysliy 'I EmployeName received from the company YourCompany the quantity of "\
            "$500.00 by concept of payslip', you need put:"),
        'sample_text': _("'account.invoice': '''I %(partner_name)s promissory note to the order "\
            "of %(company_name)s the amount of %(invoice_amount)s''', 'hr.payslip'"\
            ": '''I %(employe_name)s received from the company %(company_name)s the "\
            "quantity of %(amount_payslip)s by concept of payslip'''"),
        'sample_dict': _("'account.invoice' : {'partner_name' : obj.partner_id.name, "\
            "'company_name' : obj.company_id.name, 'invoice_amount': obj.amount}|'hr.payslip': "\
            "{'employe_name': obj.employee_id.name, 'company_name': obj.company_id.name, "\
            "'amount_payslip': obj.amount}"),
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
