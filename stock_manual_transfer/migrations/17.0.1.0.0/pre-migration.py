import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    rename_external_ids(cr)


def rename_external_ids(cr):
    """Rename group's external ID, from group_stock_manual_transfer → group_user

    This to follow usual naming conventions. The reason for the old name is first implementation
    of this was not as a standalone module.
    """
    cr.execute(
        """
        UPDATE
            ir_model_data
        SET
            name = 'group_user',
            write_uid = 1,
            write_date = NOW() at time zone 'UTC'
        WHERE
            module = 'stock_manual_transfer'
            AND name = 'group_stock_manual_transfer';
        """
    )
    if cr.rowcount:
        _logger.info(
            "Group's external ID renamed: stock_manual_transfer.group_stock_manual_transfer -> stock_manual_transfer.group_user"
        )
