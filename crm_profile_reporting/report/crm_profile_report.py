# -*- encoding: utf-8 -*-
import time
import pooler
from report import report_sxw
from tools.translate import _

class crm_report_profile(report_sxw.rml_parse):
  """
  Description about crm_report_profile
  """
  
  def __init__(self, cr, user, name, context):
    """
    Initlize a report parser, add custome methods to localcontext 
    @param cr: cursor to database
    @param user: id of current user
    @param name: name of the reports it self
    @param context: context arguments, like lang, time zone 
    """
    super(crm_report_profile, self).__init__(cr, user, name, context=context)
    self.localcontext.update({
      'time': time,
      'method':self.method_name,
    })
  
  def method_name(self, obj):
    """
    Custom method that process obj and return required data to report
    @param obj: parameter to method
    """
    
    
    
report_sxw.report_sxw(
  'report.crm.profile.reporting',
  'res.partner',
  'addons/crm_profile_reporting/report/crm_profile_report.rml',
  parser=crm_report_profile
)
