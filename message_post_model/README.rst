Message Post Log
================

This module adds an extended log in your model that appears in the mail.message
for each change made in the fields unlike the traditional way in wich Odoo did.

Features
--------

The extended log is added to your model's module in the following way:

        _name = "account.invoice"
        _inherit = ['account.invoice', 'message.post.show.all']

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
