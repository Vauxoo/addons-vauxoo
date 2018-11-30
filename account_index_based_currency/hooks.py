import logging
from openerp import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def pre_init_alter_table(cr):
    """This pre_init will create new columns in tables:
        - account_invoice: currency_rate, company_currency_rate,
        agreement_currency_rate and agreement_currency_id
        - res_company: index_based_currency_id.
        """

    _logger.info('Creating fields currency_rate, company_currency_rate, '
                 'agreement_currency_rate and agreement_currency_id on'
                 'account_invoice')
    cr.execute("""
    ALTER TABLE account_invoice
    ADD COLUMN currency_rate DECIMAL(12, 6),
    ADD COLUMN company_currency_rate DECIMAL(12, 6),
    ADD COLUMN agreement_currency_rate DECIMAL(12, 6),
    ADD COLUMN agreement_currency_id integer;
    """)

    _logger.info('Creating Constraints for agreement_currency_id '
                 'on account_invoice')
    cr.execute("""
    ALTER TABLE account_invoice
    ADD CONSTRAINT account_invoice_agreement_currency_id_fkey
    FOREIGN KEY (agreement_currency_id)
    REFERENCES res_currency(id)
    ON DELETE SET NULL
    """)

    _logger.info('Creating field index_based_currency_id on res_company')
    cr.execute("""
    ALTER TABLE res_company
    ADD COLUMN index_based_currency_id integer;
    """)

    _logger.info('Creating Constraints for index_based_currency_id'
                 'on res_company')
    cr.execute("""
    ALTER TABLE res_company
    ADD CONSTRAINT res_company_index_based_currency_id_fkey
    FOREIGN KEY (index_based_currency_id)
    REFERENCES res_currency(id)
    ON DELETE SET NULL
    """)


def pre_init_update_table(cr):
    """This pre_init will update the newly created columns with appropriate
    values in the tables.
    This is done at this stage because in databases with existing data
    letting the python code do this procedure can become a time consuming
    process for computed fields with hungry resource methods."""

    # /!\ NOTE: USD currency is used because it is the most widely used one
    env = api.Environment(cr, SUPERUSER_ID, {})
    usd = env.ref('base.USD').id
    cr.execute("UPDATE res_company SET index_based_currency_id = %s", (usd,))

    cr.execute("UPDATE account_invoice SET agreement_currency_id=currency_id")

    cr.execute("""
    UPDATE account_invoice ai2
    SET
        currency_rate=xr.ibc_rate/xr.c_rate,
        company_currency_rate=xr.ibc_rate/xr.cc_rate,
        agreement_currency_rate=xr.ibc_rate/xr.c_rate
    FROM
    (SELECT ai.id,
        COALESCE(
            (SELECT r.rate
                FROM res_currency_rate r
                WHERE r.currency_id = rc.index_based_currency_id
                AND r.name <= COALESCE(ai.date_invoice, ai.create_date)
                AND (r.company_id IS NULL OR r.company_id = ai.company_id)
                ORDER BY r.company_id, r.name DESC LIMIT 1), 1.0) AS ibc_rate,
        COALESCE(
            (SELECT r.rate
                FROM res_currency_rate r
                WHERE r.currency_id = ai.currency_id
                AND r.name <= COALESCE(ai.date_invoice, ai.create_date)
                AND (r.company_id IS NULL OR r.company_id = ai.company_id)
                ORDER BY r.company_id, r.name DESC LIMIT 1), 1.0) AS c_rate,
        COALESCE(
            (SELECT r.rate
                FROM res_currency_rate r
                WHERE r.currency_id = rc.currency_id
                AND r.name <= COALESCE(ai.date_invoice, ai.create_date)
                AND (r.company_id IS NULL OR r.company_id = ai.company_id)
                ORDER BY r.company_id, r.name DESC LIMIT 1), 1.0) AS cc_rate
    FROM account_invoice ai
    INNER JOIN res_company rc ON rc.id = ai.company_id) AS xr
    WHERE ai2.id = xr.id
        """)


def pre_init_hook(cr):
    """This pre_init_hook will create new columns on the existing tables and
    will populate them with appropriate data so that installing this module in
    database with huge amount of Invoices do not become into painful update"""
    pre_init_alter_table(cr)
    pre_init_update_table(cr)
