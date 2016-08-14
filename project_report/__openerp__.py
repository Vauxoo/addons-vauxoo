# coding: utf-8
{
    "name": "Project Status Report",
    "version": "8.0.0.1.0",
    "author": "Vauxoo",
    "category": "Tools",
    "summary": "A great way to report timesheet's consumption of time"
               "This is hr_timesheet_reports v2.0",
    "website": "http://www.vauxoo.com/",
    "license": "LGPL-3",
    "depends": [
        "hr_timesheet_sheet",
        "report",
        "user_story",
        "project_issue",
    ],
    "demo": [],
    "data": [
        "security/ir.model.access.csv",
        "report/layout.xml",
        "report/timesheet_template.xml",
        "model/project_report_view.xml",
        "model/hr_timesheet_reports_email.xml",
        "wizard/set_invoice_view.xml",
    ],
    "installable": True,
}
