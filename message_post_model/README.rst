Message Post Log
================

This module adds an extended log in any model with inheritance over an object
that create the field message_ids(mail.message) for each change made in the
fields of the model unlike the traditional way in wich Odoo did.

Features
--------

We add two server action to add o remove the feature in the model, with this
you do not requiere modify the code directly at least that you model does not
have a direct relation with mail.message

In the ir.model object we added three new fields:

    .. image:: https://drive.google.com/uc?export=view&id=0B2kzKLGF6ZvLRFYwcTBYT2ZUQ1E

    - Tracked: A boolean to indicate if the model has the track activated
    - Exclude Fields: A many2many field to indicate if you want to exclude of
      the track some fields related with the model
    - Exclude External Fields: A string to specify fields(database name) that
      does not have a direct relation with the object. This fields must be
      separaten by (,) without spaces among them. E.g
      product_uom_qty,product_uos_qty,name

    

- To add the track: 

    .. image:: https://drive.google.com/uc?export=view&id=0B2kzKLGF6ZvLSWhKOTZFVzRack0

- To remove it: 
    .. image:: https://drive.google.com/uc?export=view&id=0B2kzKLGF6ZvLZ1k5dEpBQUpDVUk

At the moment to add the track over the object in each change that a record
has, a message is left in the log

.. image:: https://drive.google.com/uc?export=view&id=0B2kzKLGF6ZvLdkY3aUpNWWJLYjA

If you want to exclude some fields of the model to avoid left a message if
these fields are changed you can use the field "Exclude Fields" explained
previously

.. image:: https://drive.google.com/uc?export=view&id=0B2kzKLGF6ZvLaUtPUnMxNE9LMDA

In some case you will need to exclude fields that does not have a direct
relation of the main model(The quantity in a line of an order) and these do not
apper in the Exclude Fields(many2many with domain). For these fields exist the
"Exclude External fields", where you will can specify this fields separate by (,) 
without spaces among them

.. image:: https://drive.google.com/uc?export=view&id=0B2kzKLGF6ZvLbUxtQlBhdTItekU


Also, if you need it, there is a testing module called message_post_test to
prove the funtionality.

Requirements:
-------------
- Go to https://github.com/Vauxoo/addons-vauxoo and download the repo in order to install message_post_model and message_post_test modules.

Contributors
------------

* José Morales <jose@vauxoo.com>

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

