import logging

from odoo.upgrade import util

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _convert_standard_price_usd_to_company_dependent(cr)


def _convert_standard_price_usd_to_company_dependent(cr):
    """Convert standard_price_usd to company-dependent."""
    util.make_field_company_dependent(
        cr,
        model="product.template",
        field="standard_price_usd",
        type="float",
        company_field="company_id",
    )
    _logger.info("standard_price_usd field has been converted to be company dependent")
