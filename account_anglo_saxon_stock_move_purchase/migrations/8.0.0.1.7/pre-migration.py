# -*- coding: utf-8 -*-

__name__ = "Setting PurchaseId related field into DB as storable field"


def migrate(cr, version):
    cr.execute("""
        ALTER TABLE account_move_line
        ADD COLUMN purchase_id integer;
    """)

    cr.execute("""
        ALTER TABLE account_move_line
        ADD CONSTRAINT account_move_line_purchase_id_fkey
        FOREIGN KEY (purchase_id)
        REFERENCES purchase_order(id)
        ON DELETE SET NULL;
    """)

    cr.execute("""
        UPDATE account_move_line aml1
        SET purchase_id = view.po_id
        FROM (
            SELECT aml.id AS aml_id, pol.order_id AS po_id
            FROM account_move_line aml
            INNER JOIN stock_move sm ON aml.sm_id = sm.id
            INNER JOIN purchase_order_line pol ON sm.purchase_line_id = pol.id
        ) AS view
        WHERE view.aml_id = aml1.id;;
    """)
