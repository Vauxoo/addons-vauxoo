import logging

_logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    cr.execute(
        'ALTER TABLE account_invoice ADD COLUMN currency_rate '
        ' DECIMAL(12, 6);'

        'ALTER TABLE account_invoice ADD COLUMN index_based_currency_rate '
        ' DECIMAL(12, 6);'

        'ALTER TABLE account_invoice ADD COLUMN company_currency_rate '
        ' DECIMAL(12, 6);'

        'ALTER TABLE account_invoice ADD COLUMN agreement_currency_rate '
        ' DECIMAL(12, 6);'
    )

    # /!\ NOTE: This second clause can be improved. Instead of using a plain 1
    cr.execute('UPDATE account_invoice SET currency_rate=1;')
    cr.execute('UPDATE account_invoice SET index_based_currency_rate=1;')
    cr.execute('UPDATE account_invoice SET company_currency_rate=1;')
    cr.execute('UPDATE account_invoice SET agreement_currency_rate=1;')
