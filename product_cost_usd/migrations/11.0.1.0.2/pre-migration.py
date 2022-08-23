def delete_inherited_views(cr):
    cr.execute("""
        DELETE FROM ir_ui_view AS iuv
        USING ir_model_data AS imd
        WHERE iuv.inherit_id=imd.res_id
        AND imd.name='view_product_template_tann_inhrt'
        AND imd.module='product_cost_usd'
        AND imd.model='ir.ui.view'
        """)


def migrate(cr, version):
    delete_inherited_views(cr)
