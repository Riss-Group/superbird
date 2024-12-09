from odoo import _, api, fields, models, tools
from collections import defaultdict

from odoo.exceptions import UserError


class ProductConfigurator(models.TransientModel):
    _inherit = "product.configurator"

    qty_available = fields.Float(
        'Quantity On Hand', digits='Product Unit of Measure')
    product_ids = fields.Many2many('product.product')

    @api.depends("product_tmpl_id", "product_tmpl_id.attribute_line_ids")
    def _compute_attr_lines(self):
        for configurator in self:
            attribute_lines = configurator.product_tmpl_id.attribute_line_ids
            configurator.attribute_line_ids = attribute_lines
            configurator.qty_available = configurator.product_tmpl_id.qty_available

    def action_product_forecast_report(self):
        template_values = self.env['product.template.attribute.value'].search([
            ('product_tmpl_id', '=', self.product_tmpl_id.id),
            ('product_attribute_value_id', 'in', self.value_ids.ids)
        ])

        products = self.env['product.product'].search([
            ('product_tmpl_id', '=', self.product_tmpl_id.id)
        ]).filtered(lambda p: all(
            tv.id in p.product_template_variant_value_ids.ids for tv in template_values) and template_values)

        if products:
            action = products[0].action_product_forecast_report()
            action['context'] = {
                'active_ids': products.ids,
                'active_id': products[0].id,
                'active_model': 'product.product',
            }
        else:
            action = self.env["ir.actions.actions"]._for_xml_id('stock.stock_forecasted_product_template_action')
            action['context'] = {
                'active_id': self.product_tmpl_id.id,
                'active_model': 'product.template',
            }

        return action

    def apply_onchange_values(self, values, field_names, field_onchange):
        rec = super().apply_onchange_values(values, field_names, field_onchange)
        values = rec.get("value")
        domain = rec.get("domain")
        product_tmpl_dict = values.get("product_tmpl_id", [])
        product_tmpl_id = False
        if product_tmpl_dict :
            product_tmpl_id = self.env["product.template"].browse(
                product_tmpl_dict['id']
            )
        if not product_tmpl_id:
            product_tmpl_id = self.product_tmpl_id
        field_names.append('qty_available')
        qty_available = product_tmpl_id.qty_available if product_tmpl_id else 0

        if values and   any(item.startswith('__attribute_') for item in list(values.keys())) :
            transformed_dict = {
                key.replace('__attribute_', ''): value
                for key, value in values.items()
                if key.startswith('__attribute_')
            }
            view_attribute_ids = list(map(int, transformed_dict.keys()))
            attribute_value_ids = list(transformed_dict.values())
            template_values = self.env['product.template.attribute.value'].search([('product_tmpl_id','=',product_tmpl_id.id),('attribute_id','in',view_attribute_ids),('product_attribute_value_id','in', attribute_value_ids)])
            qty_available = self._get_product_ids_qty_available(template_values.ids)

        values['qty_available'] = qty_available

        return {"value": values, "domain": domain}


    def _get_product_ids_qty_available(self, values):
        product_ids = self.env['product.product'].search([('product_tmpl_id','=', self.product_tmpl_id.id)])
        products = self.env['product.product']
        for product in product_ids:
            add_this_product = all(value_id in product.product_template_variant_value_ids.ids for value_id in values)
            if add_this_product:
                products += product
        if products :
            return sum(products.mapped('qty_available'))
        return 0
