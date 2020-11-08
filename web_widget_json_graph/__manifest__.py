{
    "name": "Line Graph for json fields",
    "version": "12.0.1.0.0",
    "author": "Vauxoo, "
              "Odoo Community Association (OCA)",
    "license": "LGPL",
    "category": "Hidden/Dependency",
    "summary": "Draw awesome json fields with graphs.",
    "depends": [
        'web',
    ],
    "data": [
        'views/templates.xml',
    ],
    "qweb": [
        'static/src/xml/web_widget_json_graph.xml',
    ],
    "test": [
    ],
    "auto_install": False,
    "installable": True,
    "application": False,
    "external_dependencies": {
        'python': [],
    },
}
