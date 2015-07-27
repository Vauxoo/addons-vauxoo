Product Name Untranslated
=========================

This module takes away the translation attribute from field `name` on model
product.template as sometimes results annoying to end user when duplicating
products or when changing name and no aware of the other languages.

WARNING
-------

After installing this module you should execute the following script in
order to preserve your secondary language strings, i.e., Your secondary
language is the one to be shown in the Product Names::

    UPDATE product_template
    SET name  subview.new_name
    FROM (
    SELECT pt.id AS tmpl_id, pt.name AS old_name, it.value AS new_name
    FROM product_template pt
    INNER JOIN ir_translation it ON (pt.id  it.res_id)
    WHERE it.name  'product.template,name'
    AND it.value <> pt.name
    ) subview
    WHERE subview.tmpl_id  id;

    UPDATE product_product
    SET name_template  subview.new_name_template
    FROM (
    SELECT pp.id AS product_id, pp.name_template AS old_name_template,
    pt.name AS new_name_template
    FROM product_product pp
    INNER JOIN product_template pt ON pp.product_tmpl_id  pt.id
    WHERE pp.name_template <> pt.name
    ) subview
    WHERE subview.product_id  id;
