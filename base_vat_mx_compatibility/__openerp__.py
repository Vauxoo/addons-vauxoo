# -*- coding: utf-8 -*-
{
    'name': 'VAT Number Validation',
    'version': '1.0',
    "category": 'Hidden/Dependency',
    'complexity': "easy",
    'description': """
VAT validation for Partners' VAT numbers
========================================

After installing this module, values entered in the VAT field of Partners will
be validated for all supported countries. The country is inferred from the
2-letter country code that prefixes the VAT number, e.g. ``BE0477472701``
will be validated using the Belgian rules.

There are two different levels of VAT number validation:

 * By default, a simple off-line check is performed using the known validation
   rules for the country, usually a simple check digit. This is quick and 
   always available, but allows numbers that are perhaps not truly allocated,
   or not valid anymore.
 * When the "VAT VIES Check" option is enabled (in the configuration of the user's
   Company), VAT numbers will be instead submitted to the online EU VIES
   database, which will truly verify that the number is valid and currently
   allocated to a EU company. This is a little bit slower than the simple
   off-line check, requires an Internet connection, and may not be available
   all the time. If the service is not available or does not support the
   requested country (e.g. for non-EU countries), a simple check will be performed
   instead.

Supported countries currently include EU countries, and a few non-EU countries
such as Chile, Colombia, Mexico, Norway or Russia. For unsupported countries,
only the country code will be validated.

    """,
    'author': 'OpenERP SA',
    'depends': ['account'],
    'website': 'http://www.openerp.com',
    'data': [],
    'installable': True,
    'auto_install': False,
    'certificate': '',
    'images': [],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
