from odoo.upgrade import util


def migrate(cr, version):
    remove_old_views(cr)


def remove_old_views(cr):
    """Remove conflicting views from previous versions.

    When migrating from versions <= 12.0 (before standardizing view external IDs), some views with
    the old IDs may exist in the database. Those will normally be deleted after all modules are
    updated, but since they reference old fields (e.g., ``margin_percentage``), the new views fail
    to be applied, because the old one still exist at that point.
    """
    views_to_remove = (
        "sale_margin_percentage.sale_margin_percentage_form",
        "sale_margin_percentage.sale_margin_percentage_per_line_form",
    )
    for xml_id in views_to_remove:
        util.remove_view(cr, xml_id=xml_id)
