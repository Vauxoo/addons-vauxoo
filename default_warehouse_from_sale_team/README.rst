.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Sales Team Warehouse by default
===============================

Add a field `default_warehouse` in sales team.

Create sort kind of api where any object with field called warehouse_id will
take the default value from the sales team field.

To use it simple do this:

1. inherit the class that you want to set the field warehouse_id:

    class SomeClass(models.Model):
        _name = 'some.class'
        _inherit = ['some.class', 'default.warehouse']
        warehouse_id = fields.Many2one('stock.warehouse', help='Warehouse were'
        'this object will belong to')

2. Don't forget depends of this module adding it to the list into `__openerp__.py`

The default value from this field will be the warehouse setted in the section 
If the user is not related to a sales team or not warehouse setted on the
section the default warehouse will be set using the default behavior of the
system which is assign the main warehouse.
