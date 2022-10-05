{
    "name": "Analytic Business Units",
    "version": "15.0.1.0.1",
    "category": "Accounting/Accounting",
    "summary": """If you set a business unit in you analytic account now you can have an easier way to group by that
    concept on all your analytic accounting""",
    "author": "Vauxoo",
    "website": "https://vauxoo.com",
    "license": "LGPL-3",
    "depends": [
        "account",
        "analytic",
    ],
    "data": [
        "views/account_analytic_view.xml",
        "views/account_analytic_business_view.xml",
        "views/account_analytic_line_view.xml",
        "views/account_analytic_report_view.xml",
        "views/account_move_line_view.xml",
        "security/ir.model.access.csv",
    ],
    "demo": [],
    "auto_install": False,
    "application": False,
}
