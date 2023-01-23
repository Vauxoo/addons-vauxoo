.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
    :alt: License: LGPL-3

Search Action Domain
====================

This module lets the user to use server actions as a filters in the "Favorites"
section. In other words, the user might use complex queries to search the records.

To use this kind of filter, go to:

1. Settings > Technical > Actions > Server Actions > Create

2. Select model and set the state as a Python code

3. Write a valid Python code to search records in the selected model and the domain will be taken from returned action's domain

4. Press Create As Filter button to create the filter in the selected model

5. Finally, find the created filter in "Favorites" section

Server Action:

    .. image:: ../search_action_domain/static/description/search_action_domain_action.png
       :alt: search_action_domain: Create As Filter
       :height: 350px
       :width: 900px

Filter:

    .. image:: ../search_action_domain/static/description/search_action_domain_filter.png
       :alt: search_action_domain: Filter in Favorites
       :height: 350px
       :width: 900px

Result:

    .. image:: ../search_action_domain/static/description/search_action_domain_result.png
       :alt: search_action_domain: Result after apply the filter
       :height: 350px
       :width: 900px

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/Vauxoo/addons-vauxoo/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed `feedback
<https://github.com/vauxoo/
addons-vauxoo/issues/new?body=module:%20
search_action_domain%0Aversion:%20
15.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Contributors
------------

* Tomás Álvarez <tomas@vauxoo.com>
* Francisco Luna <fluna@vauxoo.com>
* Rolando Duarte <rolando@vauxoo.com>

Maintainer
----------

.. image:: https://www.vauxoo.com/logo.png
   :alt: Vauxoo
   :target: https://vauxoo.com

This module is maintained by Vauxoo.

A latinamerican company that provides training, coaching,
development and implementation of enterprise management
systems and bases its entire operation strategy in the use
of Open Source Software and its main product is odoo.

To contribute to this module, please visit https://www.vauxoo.com.
