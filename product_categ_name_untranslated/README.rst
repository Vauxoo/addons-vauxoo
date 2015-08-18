Product Category Name Untranslated
==================================

This module takes away the translation attribute from field `name` on model
product.category as sometimes results annoying to end user when duplicating
product categories or when changing name and no aware of the other
languages.

WARNING

After installing this module you should execute the following script in
order to preserve your secondary language strings, i.e., Your secondary
language is the one to be shown in the Product Category Names

UPDATE product_category
SET name  subview.new_name
FROM (
SELECT pc.id AS ctg_id, pc.name AS old_name, it.value AS new_name
FROM product_category pc
INNER JOIN ir_translation it ON (pc.id  it.res_id)
WHERE it.name  'product.category,name'
AND it.value <> pc.name
) subview
WHERE subview.ctg_id  id;