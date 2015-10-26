.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Test Sale Team Warehouse
========================

This module will test the feature of the module sale_team_warehouse.
Should test several scenarios.

This module performs the following use cases:
1.- Testing the default basic method.
A Char type field is created in the first class, the field in
the definition itself have a default text value, this allows to
test that the native default_get method works as is expected.

2.- Testing that the overwriting default_get works.
In the second class the default_get method is overwritten, in
this case proves that although the original method was modified
can still be overridden to add additional logic.

3.- Testing that the record warehouse_id match with the
warehouse returned for the _default_warehouse method.
In the third clase a many2one type field is added related to
stock.warehouse model, the test proves that the required
condition to perform the logic of the Monkey-patch over default_get
of the sale_team_warehouse module are not set, this means that the
user do not has a sales team.
This test proves that the warehouse_id assigned over the record with a
previous default its ok because match with the corresponding
warehouse_id of the company related to the user.

4.- Testing that the record warehouse_id match with the
warehouse_id assign on the sales team of the user.
Also for the third class is proved the Monkey-patch process
but in this case establishing the proper conditions (in the user a
sales tema is set and a warehouse in the sales team corresponding
field), conditions that allow in each existing model for a field
type many2one with relation to stock.warehouse with any default
value configured to have by default the warehouse set on the sales
team of the user.
