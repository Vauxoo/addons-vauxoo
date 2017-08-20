# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute("ALTER TABLE account_invoice_line "
               "ADD COLUMN discount_amount DOUBLE PRECISION;")
    cr.execute("COMMENT ON COLUMN account_invoice_line.discount_amount "
               "IS 'Discount Amount';")
    cr.execute("UPDATE account_invoice_line "
               "SET discount_amount = discount * subtotal_wo_discount / 100")

    cr.execute("ALTER TABLE account_invoice "
               "ADD COLUMN discount_amount DOUBLE PRECISION;")
    cr.execute("COMMENT ON COLUMN account_invoice.discount_amount "
               "IS 'Discount';")
    cr.execute("UPDATE account_invoice inv "
               "SET discount_amount = view.da FROM( "
               "SELECT SUM(discount_amount) AS da, invoice_id FROM "
               "account_invoice_line GROUP BY invoice_id) AS view "
               "WHERE view.invoice_id = inv.id;")
