Multi Value Dimension
=====================

This module allows load a line graph per ordered pair in a x2many field.


.. image:: https://www.evernote.com/l/AJ5Fxuoyfn5DPZCq0oTlbakT4KWh7YisWL0B/image.png
    :alt: Screenshot

Usage
=====

Use this widget by saying::

    <field name="field_text_json" widget="json_graph" />

Use of widget example::

    <field name="values_data" widget="json_graph"/>

The JSON needs to be like::

    fields = ['field1', 'field2', 'field3', ...]
    field_x = 'field_x'
    dictionary = self.value_ids.sorted(field_x).read(fields)
    color = {
        'field1': HEXCOLOR1,
        'field2': '#FFBB78',
        'field3': '#1F77B4',
        ...
    }
    dictionary = self.value_ids.sorted(field_x).read(fields)
    content = {}
    data = []
    for field in fields:
        if field != field_x:
            content[field] = []
            for rec in dictionary:
                content[field].append({'x': rec[field_x], 'y': rec[field]})
            if field in color:
                data.append({'values': content[field], 'key': field,
                    'color': color[field]})
                continue
            data.append({'values': content[field], 'key': field})
    info = {
        'label_x': 'X Label',
        'label_y': 'Y label',
        'data': data
    }
    self.field_text_json = json.dumps(info)

JSON example::

    fields = ['sequence', 'value', 'sma', 'cma']
    field_x = 'sequence'
    dictionary = self.value_ids.sorted(field_x).read(fields)
    color = {
        'value': '#2CA02C',
        'sma': '#FFBB78'
    }
    dictionary = self.value_ids.sorted(field_x).read(fields)
    content = {}
    data = []
    for field in fields:
        if field != field_x:
            content[field] = []
            for rec in dictionary:
                content[field].append({'x': rec[field_x], 'y': rec[field]})
            if field in color:
                data.append({'values': content[field], 'key': field,
                    'color': color[field]})
                continue
            data.append({'values': content[field], 'key': field})
    info = {
        'label_x': 'Sequence',
        'label_y': '',
        'data': data
    }
    self.values_data = json.dumps(info)

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
* José Robles <josemanuel@vauxoo.com>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
    :alt: Odoo Community Association
    :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
