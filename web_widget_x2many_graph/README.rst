Multi Value Dimension
=====================

This module allows load a line graph per ordered pair in a x2many field.


.. image:: https://www.evernote.com/l/AJ5Fxuoyfn5DPZCq0oTlbakT4KWh7YisWL0B/image.png
    :alt: Screenshot

Usage
=====

Use this widget by saying::

    <field name="field_one2many_ids" widget="x2many_graph" color_field_name="HEXCOLOR">
        <graph >
            <field name="sequence"/> <!-- default name for field_x -->
             <!-- The rest of fields will be taken as Y -->
            <field name="value"/>
            <field name="sma"/>
            <field name="cma"/>
            <field name="wma"/>
        </graph>
    </field>

For example::

    <field name="value_ids" widget="x2many_graph" color_value="#2CA02C" color_sma="#FFBB78" color_cma="#1F77B4" color_wma="#D62728">
        <graph >
            <field name="sequence"/>
            <field name="value"/>
            <field name="sma"/>
            <field name="cma"/>
            <field name="wma"/>
        </graph>
    </field>

You can pass the following parameters:

field_x::

    The field which define X. (not mandatory you can set in your model a field named sequence).

field_label_x::

    Label for field_x

color_[[field_name]]::

    As much colors as fields you have in your graph view.

Known issues / Roadmap
======================

* nolabel is ignored, this image will never bring a label, by default simply use an extra separator.
* A graph will use always 100% of the width, pending the css dynamic attribute.
* The height is wired.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/web/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/web/issues/new?body=module:%20web_widget_x2many_2d_graph%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

Contributors
------------

* Nhomar Hernández <nhomar@vauxoo.com>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
    :alt: Odoo Community Association
    :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
