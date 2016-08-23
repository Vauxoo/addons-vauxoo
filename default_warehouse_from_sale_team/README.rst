.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

====================
Sales Team Warehouse
====================

Usage
=====

Add a field `default_warehouse` in sales team.

Create sort kind of api where any object with field called warehouse_id will
take the default value from the sales team field
this taking into account the team defined in `Default Sale Teams` field defined
in the res.user model.

To improve, consistency and usability we add the next features:

- If you try to add a default sale team where the user do not belongs wil throw
  you an error message: Can not set default team is do not belongs to sale team
- Add an automated action/server action to update the user default sales team
  every time that a sales teams by:

    - add user's default sale team if empty.
    - remove default sale team from user if not longer in sale team.
    - dummy write to update m2m in users to make new feature for filtering
      records.

Currently this default warehouse feature applies for sale.order,
stock.picking.type and stock.picking.

Also add a new feature for Permissions and Security: Taking advantage of the
default_warehouse field in the sales team model now we can filter the
records (picking type and picking model) to only show those records that match
with the user sale teams default_warehouse. To accomplish this I:

- add new groups to manage the records access by user:

  * Default Warehouse / Limited access to pickings (filtered by sale teams)
  * Default Warehouse / Limited access to stock pickings (filtered by sale teams)
  * Default Warehouse / Access to all picking types (filtered by sale teams)
  * Default Warehouse / Access to all pickings (filtered by sale teams)

- add new m2m field in the res.user model used in the new ir.rules.
  this onw is showed as a readonly field (only informative) to know
  the teams were the sale user belongs.
- add new ir.rule records, one for each default warehouse group. This
  one will let us to only show the records for the current user sale
  teams default_warehouse or to do not take into account the sale teams
  and show all the records to the user.

To add more models use it simple do this:

1. inherit the class that you want to set the field warehouse_id::

    class SomeClass(models.Model):
        _name = 'some.class'
        _inherit = ['some.class', 'default.warehouse']
        warehouse_id = fields.Many2one('stock.warehouse', help='Warehouse were'
        'this object will belong to')

2. Create two ir.rule to filter stock.picking and stock.picking.type taking
into account the current user warehouses. When a user is part of warehouse
teams will be able to access only the records related to that warehouses::

    <record id="rule_group_model" model="ir.rule">
        <field name="name">Limited access to model (filtered by sales teams)</field>
        <field name="model_id" search="[('model','=','model')]" model="ir.model"/>
        <field name="groups" eval"[(6, 0, [ref('xml_id_group')])]/>
        <field name="domain_force">[('warehouse_id', 'in', [team.default_warehouse.id for team in user.sale_team_ids if team.default_warehouse])]</field>
    </record>
    <record id="rule_group_model_2" model="ir.rule">
        <field name="name">Access to all model</field>
        <field name="model_id" search="[('model','=','model')]" model="ir.model"/>
        <field name="groups" eval"[(6, 0, [ref('xml_id_group')])]/>
        <field name="domain_force">[(1, '=', 1)]</field>
    </record>

3. Don't forget depends of this module adding it to the list into `__openerp__.py`

The default value from this field will be the warehouse setted in the section
If the user is not related to a sales team or not warehouse setted on the
section the default warehouse will be set using the default behavior of the
system which is assign the main warehouse.

Bug Tracker
===========

Bugs are tracked on
`GitHub Issues <https://github.com/Vauxoo/addons-vauxoo/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and
welcomed feedback
`here <https://github.com/Vauxoo/addons-vauxoo/issues/new?body=module:%20
default_warehouse_from_sale_team
%0Aversion:%20
8.0.2.0.0
%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_

Credits
=======

**Contributors**

* Nhomar Hernandez <nhomar@vauxoo.com> (Planner/Developer)
* Katherine Zaoral <kathy@vauxoo.com> (Planner/Developer)

Maintainer
==========

.. image:: https://s3.amazonaws.com/s3.vauxoo.com/description_logo.png
   :alt: Vauxoo
   :target: https://www.vauxoo.com
   :width: 200

This module is maintained by the Vauxoo.

To contribute to this module, please visit https://www.vauxoo.com.
