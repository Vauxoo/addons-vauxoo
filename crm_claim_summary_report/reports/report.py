# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright 2016 Vauxoo
#    Author : Osval Reyes <osval@vauxoo.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
from openerp.report import report_sxw
from openerp import models


class CrmClaimSummaryReport(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(CrmClaimSummaryReport, self).__init__(
            cr, uid, name, context=context)
        self.localcontext.update({
            'get_report_ctx': self.get_report_ctx,
        })

    def get_report_ctx(self, claim_type):
        supplier_id = self.get_xml_id('crm_claim_type',
                                      'crm_claim_type_supplier')
        customer_id = self.get_xml_id('crm_claim_type',
                                      'crm_claim_type_customer')
        return 'customer' if claim_type.id == customer_id else \
            ('supplier' if claim_type.id == supplier_id else 'internal')

    def get_xml_id(self, module, xml_id_str):
        return self.pool.get('ir.model.data').\
            get_object_reference(self.cr, self.uid,
                                 module, xml_id_str)[1]


class CrmClaimSummaryReportParser(models.AbstractModel):
    _name = 'report.crm_claim_summary_report.report_translated'
    _inherit = 'report.abstract_report'
    _template = 'crm_claim_summary_report.report_translated'
    _wrapped_report_class = CrmClaimSummaryReport
