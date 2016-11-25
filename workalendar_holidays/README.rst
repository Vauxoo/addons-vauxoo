.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Workalendar Holidays
====================

This module add a wizard in Work Time model, to load public holidays by a given
country. Also provide functions to compute working days.

To developers, can inherit this module as a helper to recompute planned dates
just for working days.

Installation
============

- To install this module, you should have `Workalendar
  <https://github.com/novafloss/workalendar>`_ python package. If you don't
  have it, can install with: ``pip install workalendar``

- Then, just install as a regular Odoo module:

  - Download this module from `Vauxoo/addons-vauxoo
    <https://github.com/Vauxoo/addons-vauxoo/workalendar_holidays>`_
  - Add the repository folder into your odoo addons-path.
  - Go to ``Settings > Module list`` search for the current name and click in
    *Install* button.

Usage
=====

* Select at Working Time in ``Settings > Technical > Working Time`` then click on More press *Import Holidays*

  .. image:: https://cloud.githubusercontent.com/assets/5335402/19224986/3e82d8c0-8e57-11e6-8533-a683abb0fa10.png

* Fill *Import Holidays* wizard giving it a geographic location, then press *Import*

  .. image:: https://cloud.githubusercontent.com/assets/5335402/19224988/4295431c-8e57-11e6-8c7a-374816f84037.png

* If localization is `available <https://github.com/novafloss/workalendar#available-calendars>`_  in *Workalendar* module then will be imported the holidays successfully

  .. image:: https://cloud.githubusercontent.com/assets/5335402/19224991/4741febe-8e57-11e6-962b-991faa2a66de.png

**For developers:** This module can be used as a helper to recompute planned dates to just working days. To see more about it, please check function `compute_working_days <https://github.com/Vauxoo/addons-vauxoo/blob/8.0/workalendar_holidays/models/resource.py#L100>`_. Example:

   ::

     delay = -1 * (procurement.rule_id.delay or 0)
     date_expected = work_time.compute_working_days(delay, start_dt)

Known issues / Roadmap
======================

* When you run the *Import Holiday* wizard your Odoo user must have configured
  the same time zone as the client computer from which it is being accessed,
  in order to have the hours of the holidays correctly established.
* Not tested yet in a multi-company environment


Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/Vauxoo/addons-vauxoo/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed `feedback
<https://github.com/vauxoo/
addons-vauxoo/issues/new?body=module:%20
workalendar_holidays%0Aversion:%20
8.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

TODO
----
- Highlight non working days in user Calendar: ``Messaging > Organizer >
  Calendar``
- Create a Scheduled Action to import Public Holidays every so often, to keep
  up-to-date the future company public holidays.
- At present, workalendar's library has support to local holidays from: EEUU,
  Canada, Germany. This module can be improved adding local holidays for a
  given region/state.

Contributors
------------

* Jose Suniaga <josemiguel@vauxoo.com>

Maintainer
----------

.. image:: https://www.vauxoo.com/logo.png
   :alt: Vauxoo
   :target: https://vauxoo.com

This module is maintained by Vauxoo.

a latinamerican company that provides training, coaching,
development and implementation of enterprise management
systems and bases its entire operation strategy in the use
of Open Source Software and its main product is odoo.

To contribute to this module, please visit http://www.vauxoo.com.
