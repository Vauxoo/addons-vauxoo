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
            help='This text will put in the report of Invoice'),
        'dict_var' : fields.text('Variables to use in text',
            help='Put te variables used in text'),
        'sample_text' : fields.text('Promissory note', readonly=True),
        'sample_dict' : fields.text('Variables to use in text', readonly=True),
        'details' : fields.text('Variables to use in text', readonly=True),
        'sample' : fields.text('Variables to use in text', readonly=True),
    }
    
    _defaults = {
        'details' : _("In the field 'Promissory note' you need put the text "\
            "that you like that was colocate in the report as promissory, if "\
            "you like take a data from the parner, company or the invoice "\
            "you need create a new variable in the field 'Variables to use "\
            "in text' as follows : \n'name_variable' : object.value of object, "\
            "and when you need use an variable you put %(variable)s for use "\
            "information from an object. \nWhen you need information from "\
            "the partner, use partner.field that you need from the partner, "\
            "for company use company.field an equal for an field from invoice."\
            "\nNOTE: If you need use symbol '%', you need use %%."),
        'sample' : _('If you like put the text \nI Partner pay to the order of '\
            'My Company the amount of $500.00, you need put:'),
        'sample_text' : _("'I %(partner_name)s pay to the order of %(company_"\
            "name)s the amount of %(invoice_amount)s'"),
        'sample_dict' : _("'partner_name' : partner.name, 'company_name' : "\
            "company.name, 'invoice_amount' : invoice.amount_total"),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
