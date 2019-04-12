# coding: utf-8
#
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#
#    Coded by: Sabrina Romero (sabrina@vauxoo.com)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import
import functools
import itertools
import logging
import operator
from ast import literal_eval
from odoo.exceptions import UserError
from odoo import fields, models, SUPERUSER_ID, api, _

_logger = logging.getLogger('base.product.merge')


def is_integer_list(ids):
    return all(isinstance(i, (int)) for i in ids)


class MergeProductLine(models.TransientModel):
    _name = 'base.product.merge.line'
    _order = 'min_id asc'

    wizard_id = fields.Many2one(
        'base.product.merge.automatic.wizard',
        'Wizard')
    min_id = fields.Integer('MinID')
    aggr_ids = fields.Char('Ids', required=True)


class MergeProductAutomatic(models.TransientModel):
    _name = 'base.product.merge.automatic.wizard'

    group_by_name_template = fields.Boolean('Nombre')
    group_by_default_code = fields.Boolean('Referencia')
    group_by_categ_id = fields.Boolean('Categoria')
    group_by_uom_id = fields.Boolean('Unidad de medida')
    state = fields.Selection([('option', 'Option'),
                              ('selection', 'Selection'),
                              ('finished', 'Finished')],
                             readonly=True,
                             default='option',
                             required=True)
    number_group = fields.Integer("Group of Products",
                                  readonly=True)
    current_product_id = fields.Many2one('product.product',
                                         string='Current product')
    product_from = fields.Many2one('product.product')
    product_to = fields.Many2one('product.product')
    current_line_id = fields.Many2one('base.product.merge.line',
                                      'Current Line')
    line_ids = fields.One2many('base.product.merge.line',
                               'wizard_id', 'Lines')
    dst_product_id = fields.Many2one('product.product',
                                     string='Destination Contact')
    product_ids = fields.Many2many(
        'product.product', 'product_rel', 'product_merge_id',
        'product_id', string="Products to merge")
    maximum_group = fields.Integer("Maximum of Group of Contacts")

    @api.model
    def get_fk_on(self, table, tables=None):
        tables = tables and tuple(tables) or []
        where = tables and 'AND cli.relname in %s' % (str(tables))
        query = """  SELECT cl1.relname as table,
                        att1.attname as column
                   FROM pg_constraint as con, pg_class as cl1, pg_class as cl2,
                        pg_attribute as att1, pg_attribute as att2
                  WHERE con.conrelid = cl1.oid
                    AND con.confrelid = cl2.oid
                    AND array_lower(con.conkey, 1) = 1
                    AND con.conkey[1] = att1.attnum
                    AND att1.attrelid = cl1.oid
                    AND cl2.relname = %s
                    AND att2.attname = 'id'
                    AND array_lower(con.confkey, 1) = 1
                    AND con.confkey[1] = att2.attnum
                    AND att2.attrelid = cl2.oid
                    AND con.contype = 'f'
                    %s
        """
        self.env.cr.execute(query, (table, tables and where or '',))
        return self.env.cr.fetchall()

    @api.multi
    def _update_foreign_keys(self, src_products, dst_product, model=None):
        if model:
            return self._update_foreign_keys_modify(
                src_products, dst_product, model=model)
        # find the many2one relation to a product
        proxy = self.env['product.product']
        uom_ids = self.env['product.uom'].search([
            ('category_id', '=', dst_product.uom_id.category_id.id)]).ids

        res = self.get_fk_on('product_uom')
        product_bad = []
        record = []
        flag = []
        uos_table = {}
        for table, column in res:
            if table in uos_table:
                record = uos_table.get(table, [])
                record.append(column)
                uos_table.update({table: record})
            else:
                uos_table.update({table: [column]})
        res = self.get_fk_on('product_product')

        for table, column in res:
            if 'base_product_merge_' in table:
                continue

            product_ids = tuple([int(i) for i in src_products.ids])

            query = """SELECT column_name FROM information_schema.columns
                        WHERE table_name LIKE '%s'""" % (table)
            self.env.cr.execute(query, ())
            columns = []
            for data in self.env.cr.fetchall():
                if data[0] != column:
                    columns.append(data[0])

            query_dic = {
                'table': table,
                'column': column,
                'value': columns[0],
            }
            if len(columns) <= 1:
                # unique key treated
                query = """
                    UPDATE "%(table)s" as ___tu
                    SET %(column)s = %%s
                    WHERE
                        %(column)s = %%s AND
                        NOT EXISTS (
                            SELECT 1
                            FROM "%(table)s" as ___tw
                            WHERE
                                %(column)s = %%s AND
                                ___tu.%(value)s = ___tw.%(value)s
                        )""" % query_dic
                for product_id in product_ids:
                    self.env.cr.execute(query, (
                        dst_product.id, product_id, dst_product.id))
            else:
                self.env.cr.execute(
                    "SAVEPOINT recursive_product_savepoint")

                if table not in uos_table:
                    query = '''UPDATE "%(table)s" SET %(column)s = %%s
                                WHERE %(column)s IN %%s''' % query_dic
                    self.env.cr.execute(
                        query, (dst_product.id, product_ids,))
                    if column == proxy._parent_name and \
                            table == 'product_product':
                        query = """
                        WITH RECURSIVE cycle(id, product_id) AS (
                                SELECT id, product_id
                                FROM product_product
                            UNION
                                SELECT  cycle.id,
                                        product_product.parent_id
                                FROM  product_product, cycle
                                WHERE product_product.id = cycle.parent_id
                                        AND cycle.id != cycle.parent_id
                        )
                        SELECT id FROM cycle
                        WHERE id = parent_id AND id = %s
                        """
                        self.env.cr.execute(query, (dst_product.id,))
                        if self.env.cr.fetchall():
                            self.env.cr.execute(
                                "ROLLBACK TO SAVEPOINT "
                                "recursive_product_savepoint")
                else:
                    query = '''SELECT *
                                FROM "%(table)s"
                                WHERE %(column)s IN %%s''' % query_dic
                    self.env.cr.execute(query, (product_ids,))
                    # Validation with flag
                    for match in self.env.cr.dictfetchall():
                        uos_field = uos_table.get(table)
                        uos_id = [match.get(i) for i in uos_field
                                  if match.get(i, False)]
                        if all([(i in uom_ids) for i in uos_id]):
                            continue
                        else:
                            flag.append(False)
                    # Handle exception for the flag validation
                    if False in flag:
                        raise UserError(
                            _("""You must verify the units of measurement
                                in which the products do you wish to merge
                                already have operations."""))
                    else:
                        self.env.cr.execute(query, (product_ids,))
                        for match in self.env.cr.dictfetchall():
                            uos_field = uos_table.get(table)
                            uos_id = [match.get(i) for i in uos_field
                                      if match.get(i, False)]
                            if all([(i in uom_ids) for i in uos_id]):
                                query = '''UPDATE "%(table)s"
                                            SET %(column)s = %%s
                                            WHERE id=%%s''' % query_dic
                                self.env.cr.execute(
                                    query, (dst_product.id,
                                            match.get('id'),))
                                if column == proxy._parent_name and \
                                        table == 'product_product':
                                    query = """
                        WITH RECURSIVE cycle(id, product_id)
                        AS (SELECT id, product_id
                            FROM product_product
                            UNION
                                SELECT  cycle.id,
                                        product_product.parent_id
                                FROM product_product, cycle
                                WHERE product_product.id = cycle.parent_id
                                        AND cycle.id != cycle.parent_id
                        )
                        SELECT id FROM cycle
                        WHERE id = parent_id AND id = %s
                                    """
                                    self.env.cr.execute(
                                        query, (dst_product.id,))
                                    if self.env.cr.fetchall():
                                        self.env.cr.execute(
                                            "ROLLBACK TO SAVEPOINT "
                                            "recursive_product_savepoint")
                            else:
                                product_bad.append(
                                    match.get(query_dic.get('column')))
        return product_bad

    @api.model
    def _update_foreign_keys_modify(
            self, src_products, dst_product, model=None):
        uos_table = {}
        po_table = {}
        tables = []
        product_ids_validate = []
        product_ids_unvalidate = []

        product_obj = self.env['product.product']
        proxy = self.env[model.replace('_', '.') or 'product.uom']
        dst_product_ids = product_obj.browse(
            self.env.context.get('active_ids'))
        uom_factor_dst = self.env['product.uom'].browse(dst_product)[0].factor
        for dst_product_id in dst_product_ids:
            if dst_product_id.uom_id.factor == uom_factor_dst:
                product_ids_validate.append(dst_product_id.id)
            else:
                product_ids_unvalidate.append(dst_product_id.name)
        dst_product = dst_product[0]

        res = self.get_fk_on('product_uom')
        for table, column in res:
            tables.append(table)
            if table in uos_table:
                val = uos_table.get(table, [])
                val.append(column)
                uos_table.update({table: val})
            else:
                uos_table.update({table: [column]})

        res = self.get_fk_on('product_product', tables)
        for table, column in res:
            if table in po_table:
                val = po_table.get(table, [])
                val.append(column)
                po_table.update({table: val})
            else:
                po_table.update({table: [column]})

        if len(product_ids_validate) > 0:
            for table in uos_table:

                if 'base_product_merge_' in table:
                    continue

                product_ids = tuple(product_ids_validate)

                querys = """SELECT column_name FROM information_schema.columns
                           WHERE table_name LIKE '%s'""" % (table)

                columns = []
                for column in po_table.get(table, False) and \
                        uos_table.get(table) or []:
                    self.env.cr.execute(querys, ())
                    for data in self.env.cr.fetchall():
                        if data[0] != column:
                            columns.append(data[0])

                    query_dic = {
                        'table': table,
                        'column': column,
                        'param': po_table.get(table)[0],
                        'value': columns[0],
                    }

                    if len(columns) <= 1:
                        # unique key treated
                        query = """
                            UPDATE "%(table)s" as ___tu
                            SET %(column)s = %%s
                            WHERE
                                %(param)s IN %%s AND
                                NOT EXISTS (
                                    SELECT 1
                                    FROM "%(table)s" as ___tw
                                    WHERE
                                        %(param)s IN %%s AND
                                        ___tu.%(value)s = ___tw.%(value)s
                                )""" % query_dic
                        self.env.cr.execute(query, (
                            dst_product, product_ids, product_ids))
                    else:
                        self.env.cr.execute(
                            "SAVEPOINT recursive_product_savepoint")

                        query = '''UPDATE "%(table)s" SET %(column)s = %%s
                                   WHERE %(param)s IN %%s''' % query_dic
                        self.env.cr.execute(query, (dst_product, product_ids))
                        if (column == proxy._parent_name and
                                table == 'product_uom'):

                            query = """
                                WITH RECURSIVE cycle(id, product_id) AS (
                                        SELECT id, product_id FROM %s
                                    UNION
                                       SELECT  cycle.id, %s.parent_id
                                       FROM    %s, cycle
                                       WHERE   %s.id = cycle.parent_id AND
                                                cycle.id != cycle.parent_id
                                )
                                SELECT id FROM cycle
                                WHERE id = parent_id AND id = %%s
                            """ % (model, model, model, model)
                            self.env.cr.execute(query, (dst_product,))
                            if self.env.cr.fetchall():
                                self.env.cr.execute(
                                    "ROLLBACK TO SAVEPOINT "
                                    "recursive_product_savepoint")
        return True

    def _update_reference_fields(self, src_products, dst_product):
        product_bad = []

        def update_records(model, src, field_model='model', field_id='res_id'):
            proxy = self.env[model]
            if proxy is None:
                return
            domain = [(field_model, '=', 'product.product'), (
                field_id, '=', src.id)]
            proxy_ids = proxy.sudo().search(domain)
            return proxy_ids.write({field_id: dst_product.id})

        update_records = functools.partial(update_records)

        proxy = self.env['ir.model.fields']
        domain = [('ttype', '=', 'reference')]
        record_ids = proxy.search(domain)

        for record in record_ids:
            proxy_model = self.env[record.model]

            field_type = proxy_model._fields.get(record.name).type

            if field_type == 'function':
                continue

            for product in src_products:
                domain = [
                    (record.name, '=', 'product.product,%d' % product.id)
                ]
                model_ids = proxy_model.search(domain)
                values = {
                    record.name: 'product.product,%d' % dst_product.id,
                }
                model_ids.write(values)
        return product_bad

    def _update_values(self, src_products, dst_product):
        product_bad = []
        columns = dst_product._fields

        def write_serializer(column, item):
            if isinstance(item, models.BaseModel):
                return item.id
            else:
                return item

        values = dict()
        for column, field in columns.items():
            if (field.type not in ('many2many', 'one2many') and not
                    field.compute):
                for item in itertools.chain(src_products, [dst_product]):
                    if item[column]:
                        values[column] = write_serializer(column, item[column])

        values.pop('id', None)
        parent_id = values.pop('parent_id', None)
        dst_product.write(values)
        if parent_id and parent_id != dst_product.id:
            try:
                dst_product.write({'parent_id': parent_id})
            except:
                _logger.info(
                    '''Skip recursive product hierarchies
                       for parent_id %s of product: %s''', parent_id,
                    dst_product.id)
        return product_bad

    @api.multi
    def close_cb(self):
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def _merge(self, product_ids, dst_product=None):
        proxy = self.env['product.product']
        product_ids = proxy.browse(product_ids).exists()
        if len(product_ids) < 2:
            return True

        if len(product_ids) > 10:
            raise UserError(
                _("""For safety reasons, you cannot merge more than 10 products
                  together. You can re-open the wizard several times if needed.
                  """))
        if dst_product and dst_product in product_ids:
            src_products = product_ids.filtered(lambda x: x != dst_product)
        else:
            ordered_products = self._get_ordered_product(product_ids.ids)
            dst_product = ordered_products[-1]
            src_products = ordered_products[:-1]
        _logger.info("dst_product: %s", dst_product.id)

        if SUPERUSER_ID != self.env.uid and \
                self._model_is_installed('account.move.line') and \
                self.env['account.move.line'].sudo().search([
                    ('product_id', 'in', [
                        product.id for product in src_products])]):
            raise UserError(
                _("""Only the destination product may be linked to existing
                  Journal Items. Please ask the Administrator if you need to
                  merge several products linked to existing Journal Items."""))
        product_bad = []

        product_bad += self._update_foreign_keys(src_products, dst_product)
        product_bad += self._update_reference_fields(src_products, dst_product)
        product_bad += self._update_values(src_products, dst_product)
        product_bad = set(product_bad)
        for product in src_products:
            if product.id not in product_bad:
                product.unlink()
                product.exists()
        return True

    @api.model
    def _get_ordered_product(self, product_ids):
        products = self.env['product.product'].browse(list(product_ids))
        ordered_products = sorted(
            sorted(products, key=operator.attrgetter('create_date'),
                   reverse=True),
            key=operator.attrgetter( 'active'), reverse=True)
        return ordered_products

    @api.model
    def _model_is_installed(self, model):
        proxy = self.env['ir.model']
        domain = [('model', '=', model)]
        return proxy.search_count(domain) > 0

    @api.multi
    def merge_cb(self):
        self.ensure_one()

        p_ids = self.product_ids and self.product_ids.ids
        if p_ids:
            p_ids.append(self.product_to)
        product_ids = set([int(i) for i in self.product_from and
                           [self.product_to, self.product_from] or p_ids])
        if not list(product_ids):
            raise UserError(
                _("""The product from must be selected for this option."""))
        self._merge(product_ids, self.product_to)
        return True

    @api.multi
    def _compute_selected_groupby(self):
        group_by_str = 'group_by_'
        group_by_len = len(group_by_str)

        lfields = [
            key[group_by_len:]
            for key in self._fields.keys()
            if key.startswith(group_by_str)
        ]

        groups = [
            field
            for field in lfields
            if getattr(self, '%s%s' % (group_by_str, field), False)
        ]

        if not groups:
            raise UserError(
                _("""You have to specify a filter for your selection."""))
        return groups

    def _generate_query(self, lfields, maximum_group=100):
        group_fields = ', '.join(lfields)

        filters = []
        for field in lfields:
            if field in ['name_template', 'default_code', ]:
                filters.append((field, 'IS NOT', 'NULL'))

        criteria = ' AND '.join('%s %s %s' % (field, operator, value)
                                for field, operator, value in filters)

        text = [
            "SELECT min(id), array_agg(id)",
            "FROM product_product",
        ]

        if criteria:
            text.append('WHERE %s' % criteria)

        text.extend([
            "GROUP BY %s" % group_fields,
            "HAVING COUNT(*) >= 2",
            "ORDER BY min(id)",
        ])

        if maximum_group:
            text.extend([
                "LIMIT %s" % maximum_group,
            ])

        return ' '.join(text)

    @api.multi
    def _process_query(self, query):
        """Execute the select request and write the result in this wizard
        """
        self.ensure_one()
        proxy = self.env['base.product.merge.line']
        self.env.cr.execute(query)

        counter = 0
        for min_id, aggr_ids in self.env.cr.fetchall():

            values = {
                'wizard_id': self.id,
                'min_id': min_id,
                'aggr_ids': aggr_ids,
            }
            proxy.create(values)
            counter += 1

        values = {
            'state': 'selection',
            'number_group': counter,
        }

        self.write(values)

        _logger.info("counter: %s", counter)

    @api.model
    def _next_screen(self, this):
        this.refresh()
        values = {}
        if this.line_ids:
            # in this case, we try to find the next record.
            current_line = this.line_ids[0]
            current_product_ids = literal_eval(current_line.aggr_ids)
            values.update({
                'current_line_id': current_line.id,
                'product_ids': [(6, 0, current_product_ids)],
                'product_to': self.
                _get_ordered_product(current_product_ids)[-1].id,
                'state': 'selection',
            })
        else:
            values.update({
                'current_line_id': False,
                'product_ids': [],
                'state': 'finished',
            })

        this.write(values)

        return {
            'type': 'ir.actions.act_window',
            'res_model': this._name,
            'res_id': this.id,
            'view_mode': 'form',
            'target': 'new',
        }

    @api.multi
    def other_screen(self):
        self.ensure_one()
        self.refresh()
        obj_model = self.env['ir.model.data']
        values = {}
        if self.line_ids:
            # in this case, we try to find the next record.
            current_line = self.line_ids[0]
            current_product_ids = literal_eval(current_line.aggr_ids)
            values.update({
                'current_line_id': current_line.id,
                'product_ids': [(6, 0, current_product_ids)],
                'product_to': self._get_ordered_product(
                    current_product_ids)[-1].id,
                'state': 'selection',
            })
        else:
            values.update({
                'current_line_id': False,
                'product_ids': [],
                'state': 'finished',
            })
        self.write(values)
        model_data_ids = obj_model.search([
            ('model', '=', 'ir.ui.view'),
            ('name', '=', 'base_product_merge_automatic_wizard_form_two')])
        resource_id = model_data_ids.read(fields=['res_id'])[0]['res_id']

        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'base.product.merge.automatic.wizard',
            'res_id': self.id,
            'views': [(resource_id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    @api.multi
    def start_process_cb(self):
        """Start the process.
        * Compute the selected groups (with duplication)
        * If the user has selected the 'exclude_XXX' fields, avoid the
        products.
        """
        self.ensure_one()
        groups = self._compute_selected_groupby()
        query = self._generate_query(groups, self.maximum_group)
        self.with_context(active_test=False)._process_query(query)
        return self.with_context(active_test=False).other_screen()

    @api.multi
    def next_cb(self):
        """Don't compute any thing
        """
        self.ensure_one()
        if self.current_line_id:
            self.current_line_id.unlink()
        return self.other_screen()
