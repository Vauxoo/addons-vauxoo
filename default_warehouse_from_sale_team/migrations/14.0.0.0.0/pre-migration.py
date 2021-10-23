import logging

from odoo import tools

_logger = logging.getLogger()


def migrate(cr, version):
    rename_default_warehouse(cr)


def rename_default_warehouse(cr):
    """Rename field ``default_warehouse`` from sales teams to add the correct suffix"""
    table_name = "crm_team"
    old_field = "default_warehouse"
    new_field = "default_warehouse_id"
    if not tools.column_exists(cr, table_name, old_field):
        return
    _logger.info("Renaming database column on table %s: %s -> %s", table_name, old_field, new_field)
    tools.rename_column(cr, table_name, old_field, new_field)
