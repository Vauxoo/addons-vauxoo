# -*- encoding: utf-8 -*-
import time
from openerp.report import report_sxw


class openacademy_course(report_sxw.rml_parse):

    """
    Description about openacademy_course
    """

    def __init__(self, cr, user, name, context):
        """
        Initlize a report parser, add custome methods to localcontext
        @param cr: cursor to database
        @param user: id of current user
        @param name: name of the reports it self
        @param context: context arguments, like lang, time zone
        """
        super(openacademy_course, self).__init__(cr, user, name, context=context)
        self.localcontext.update({
            'time': time,
            'como_lo_llamare': self.metodo_que_llamare,
        })

    def metodo_que_llamare(self, obj):
        """
        Custom method that process obj and return required data to report
        @param obj: parameter to method
        """
        # procesos del negocio
        print "en el reporte %s" % obj
        return "Lo que quiero que devuelva %s" % obj


report_sxw.report_sxw(
    'report.course.report',
    'openacademy.course',
    'addons/openacademy/report/openacademy_course.rml',
    parser=openacademy_course
)
