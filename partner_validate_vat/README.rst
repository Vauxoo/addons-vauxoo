.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

====================
Partner Validate VAT
====================

This module validate that Partner's VAT must be a unique value in each company

Requirements:
-------------
- Go to https://github.com/Vauxoo/addons-vauxoo and download repo in order to install base_vat_country module.


* Before to install
  If the following sql returns records you will can not install it:

.. code-block:: sql

  SELECT lower(regexp_replace(vat, '\W', '', 'g')), company_id, count(*) AS repeated 
  FROM res_partner 
  WHERE vat IS NOT NULL 
    AND (parent_id is NULL OR is_company) 
  GROUP BY lower(regexp_replace(vat, '\W', '', 'g')), company_id 
  HAVING count(*) >=2


Contributors
------------

* Julio Serna <julio@vauxoo.com> (Planner/Auditor)
* Deivis Laya <deivis@vauxoo.com> (Developer)

Maintainer
----------

.. image:: https://www.vauxoo.com/logo.png
   :alt: Vauxoo
   :target: https://vauxoo.com
   :width: 200

This module is maintained by Vauxoo.

A latinamerican company that provides training, coaching,
development and implementation of enterprise management
sytems and bases its entire operation strategy in the use
of Open Source Software and its main product is odoo.

To contribute to this module, please visit http://www.vauxoo.com.

