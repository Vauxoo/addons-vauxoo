--Fix invoice number
UPDATE account_invoice
SET internal_number = inv2.number
FROM account_invoice inv2
WHERE account_invoice.internal_number IS NULL
  AND inv2.number IS NOT NULL
  AND inv2.id = account_invoice.id
;

UPDATE account_invoice
SET number = inv2.internal_number
FROM account_invoice inv2
WHERE inv2.internal_number IS NOT NULL
  AND account_invoice.number IS NULL
  AND inv2.id = account_invoice.id
;

--Recovery invoice number when state is cancel
SELECT account_invoice.id AS invoice_id, ir_attachment.name--account_invoice.number, account_invoice.internal_number
FROM account_invoice
LEFT OUTER JOIN ir_attachment
  ON ir_attachment.res_model = 'account.invoice'
  AND ir_attachment.res_id = account_invoice.id
WHERE account_invoice.state = 'cancel'
  AND (internal_number IS NULL 
   OR number IS NULL)
AND ir_attachment.name ILIKE '%.xml%'
;

SELECT *
FROM ir_attachment
WHERE res_model = 'account.invoice'
and
  
WHERE account_invoice.internal_number IS NULL
  AND account_invoice.number IS NOT NULL
  AND account_invoice.id = account_invoice.id




SELECT account_invoice.id AS invoice_id, ir_attachment.name--account_invoice.number, account_invoice.internal_number
FROM account_invoice
LEFT OUTER JOIN ir_attachment
  ON ir_attachment.res_model = 'account.invoice'
  AND ir_attachment.res_id = account_invoice.id
WHERE account_invoice.state = 'cancel'
  AND (internal_number IS NULL 
   OR number IS NULL)
AND ir_attachment.name ILIKE '%.xml%'
;
