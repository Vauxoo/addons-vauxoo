.. image:: https://img.shields.io/badge/license-LGPL--3-blue.png
    :alt: License: LGPL-3
    :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html

===========================
Sync User Login With E-Mail
===========================

This module ensures the e-mail address of a contact associated with an internal
user remains synchronized with the user's login.

**Why?**

It is natively possible for an internal user to edit the e-mail of the contact
associated to their user. This could be a security risk, because someone could
(accidentally?) change their own e-mail to an address different from the one
used to sign up (e.g. an e-mail outside the organization), which could lead to
an external person to receive sensitive information or intended to be sent only
to internal users.

To prevent the above, this module disables editing e-mails of contacts
associated with internal users if their e-mail matches their user login. Now, to
edit an e-mail, you will need to edit the user login, which will update contact
e-mails automatically, ensuring both login and e-mail are synced.

This adds two security layers:

- It prevents accidental or unauthorized changes to contact e-mails.
- It restricts e-mail modifications to administrators, as only they have
  permission to edit user records.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/Vauxoo/addons-vauxoo/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us to smash it by providing a detailed and welcomed
`feedback
<https://github.com/vauxoo/addons-vauxoo/issues/new?body=
module:%20base_sync_login_email%0A
version:%2016.0%0A%0A
**Steps%20to%20reproduce**%0A
-%20...%0A%0A
**Current%20behavior**%0A%0A
**Expected%20behavior**>`_.

Do not contact contributors directly about support or help with technical issues.

Credits
=======

Contributors
------------

* Luis González <lgonzalez@vauxoo.com>

Maintainers
-----------

This module is maintained by Vauxoo.

.. image:: https://www.vauxoo.com/logo.png
   :alt: Vauxoo
   :target: https://vauxoo.com

A latinamerican company that provides training, coaching,
development and implementation of enterprise management
systems and bases its entire operation strategy in the use
of Open Source Software and its main product is odoo.

To contribute to this module, please visit https://www.vauxoo.com.
