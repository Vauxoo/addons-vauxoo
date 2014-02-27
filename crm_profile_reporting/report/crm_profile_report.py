# -*- encoding: utf-8 -*-
import time
import pooler
from report import report_sxw
from openerp.tools.translate import _

import smtplib
import mimetypes
import base64
from email.MIMEText import MIMEText
from email.Encoders import encode_base64


class crm_report_profile(report_sxw.rml_parse):
    """
    Description about crm_report_profile
    """

    def __init__(self, cr, uid, name, context=None):
        """
        Initlize a report parser, add custome methods to localcontext
        @param cr: cursor to database
        @param user: id of current user
        @param name: name of the reports it self
        @param context: context arguments, like lang, time zone
        """
        super(crm_report_profile, self).__init__(
            cr, uid, name, context=context)
        self.localcontext.update({
                                 'time': time,
                                 })

report_sxw.report_sxw(
    'report.crm.profile.reporting',
    'res.partner',
    'addons/crm_profile_reporting/report/crm_profile_report.rml',
    parser=crm_report_profile
)
