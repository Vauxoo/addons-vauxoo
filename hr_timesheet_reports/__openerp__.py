# -*- encoding: utf-8 -*-
{
    "name": "Timesheet reports used internally",
    "version": "1.5",
    "author": "Vauxoo",
    "category": "Tools",
    "summary": "A great way to report timesheet's consumption of time",
    "website": "http://www.vauxoo.com/",
    "license": "AGPL-3",
    "depends": [
        "hr_timesheet_sheet",
        "report_webkit",
        "report",
        "user_story",
        "project_issue",
    ],
    "demo": [],
    "data": [
        "report/layout.xml",
        "report/timesheet_template.xml",
        "model/hr_timesheet_reports_view.xml",
        "model/hr_timesheet_reports_email.xml",
        "wizard/set_invoice_view.xml",
    ],
    "installable": True,
    "active": False,
}
