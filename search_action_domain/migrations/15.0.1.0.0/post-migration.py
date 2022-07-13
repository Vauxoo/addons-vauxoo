import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    convert_export_reference_to_search_action_domain_for_filter(cr)


def convert_export_reference_to_search_action_domain_for_filter(cr):
    cr.execute(
        """
        UPDATE
            ir_model_data
        SET
            module = 'search_action_domain',
            noupdate = TRUE
        WHERE
            name like 'ir_filters_server_action_%'
            AND module = '__export__'
        """
    )
    _logger.info(
        "%s records from ir_model_data were updated from __export__ to search_action_domain",
        cr.rowcount,
    )
