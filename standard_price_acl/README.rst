Overwrite field standard_price
==============================

Fixed groups on field 'standard_price'

This module is created because in the definiton of field
**standard_price** on the module product.product, the asignation of groups is
made in `file product.py` in model definition::

    'standard_price': fields.float(
        'Cost',
        digits_computedp.get_precision('Product Price'),
        groups"base.group_user",
        help="Cost price of the product used for standard stock valuation in accounting and used as a base price on purchase orders.",
    ),

This way forces to allows work with the groups **base.group_user**.
