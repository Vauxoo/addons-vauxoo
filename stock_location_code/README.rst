.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Stock Location Code
===================

Add the code field to the location model. The location code is unique per
company and will fo with the location name always. This way when searching a
a location you can search it by name or code. The location record will be
show "[code] name" location in the many2one fields (This emule the product
model of product module).

New Feature
-----------

#. When you search a location by code or name if is it related to a warehouse, it is shown like (Warehouse).

#. e.g. [code] name (warehouse)

Requirements:
-------------
- Go to https://github.com/Vauxoo/addons-vauxoo and download the repo in order to install stock_location_code.

Maintainer
----------

.. image:: https://www.vauxoo.com/logo.png
   :alt: Vauxoo
   :target: https://vauxoo.com

This module is maintained by Vauxoo.

A latinamerican company that provides training, coaching,
development and implementation of enterprise management
sytems and bases its entire operation strategy in the use
of Open Source Software and its main product is odoo.

To contribute to this module, please visit http://www.vauxoo.com.
