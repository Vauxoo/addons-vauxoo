# coding: utf-8
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: hugo@vauxoo.com
#    planned by: Nhomar Hernandez <nhomar@vauxoo.com>
############################################################################

from openerp import models, api


class ProcurementOrder(models.Model):

    _inherit = "procurement.order"

    @api.model
    def _create_service_task(self, procurement):
        task_id = super(ProcurementOrder, self)._create_service_task(
            procurement)
        sale_line = procurement.sale_line_id
        planned_hours = sale_line.estimated_hours * sale_line.product_uom_qty
        project_task = self.env['project.task'].browse(task_id)
        project_task.write({
            'planned_hours': planned_hours},)
        return task_id
