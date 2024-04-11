import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    update_margin_threshold(env)
    recompute_margin_percent(env)


def update_margin_threshold(env):
    companies = env["res.company"].search([])
    for company in companies:
        company.write({"margin_threshold": company.margin_threshold / 100.0})

    _logger.info("The margin threshold for %s companies have been updated.", len(companies))


def recompute_margin_percent(env):
    order_lines = env["sale.order.line"].search([])
    order_lines._compute_margin()
    _logger.info("The margin percentage of %s records have been recomputed.", len(order_lines))
