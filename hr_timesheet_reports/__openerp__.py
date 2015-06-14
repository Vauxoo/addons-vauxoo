# -*- encoding: utf-8 -*-
{
    "name": "Timesheet reports used internally",
    "version": "1.0",
    "author": "Vauxoo",
    "category": "Tools",
    "summary": "A great way to report timesheet's consumption of time",
    "description": """
Timesheet reports:
==================

1.- Wizard to report timesheets to deliver to customers well presented and
correctly ordered and audited.

a. Filter between dates.
b. Group by month, by user or by analytic account.
c. Deliver how much was consumed by user story.

2.- Improve your communication to your customers delivering directly this
report.

3.- Save your reports to use them as auditory process.
    """,
    "website": "http://www.vauxoo.com/",
    "license": "AGPL-3",
    "depends": [
        "hr_timesheet_sheet",
        "report_webkit",
        "user_story",
        "project_issue",
    ],
    "demo": [],
    "data": [
        "model/hr_timesheet_reports_formats.xml",
        "model/hr_timesheet_reports_view.xml",
        "model/hr_timesheet_reports_email.xml",
        "wizard/set_invoice_view.xml",
    ],
    "installable": True,
    "active": False,
}
