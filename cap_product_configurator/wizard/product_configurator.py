from odoo import _, api, fields, models


class ProductConfigurator(models.TransientModel):
    _inherit = "product.configurator"

    qty_available = fields.Float(
        'Quantity On Hand', digits='Product Unit of Measure', related="config_session_id.qty_available")
    product_ids = fields.Many2many('product.product')
    lot_ids = fields.Html(related="config_session_id.lot_ids")

    @api.depends("product_tmpl_id", "product_tmpl_id.attribute_line_ids")
    def _compute_attr_lines(self):
        for configurator in self:
            attribute_lines = configurator.product_tmpl_id.attribute_line_ids
            configurator.attribute_line_ids = attribute_lines

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
                'target': 'new',
            }

        return action


    def apply_onchange_values(self, values, field_names, field_onchange):
        rec = super().apply_onchange_values(values, field_names, field_onchange)
        values = rec.get("value")
        domain = rec.get("domain")

        if values and   any(item.startswith('__attribute_') for item in list(values.keys())) :
            transformed_dict = {
                key: value
                for key, value in values.items()
                if key.startswith('__attribute_')
            }

            if self and self.config_session_id :
                self.config_session_id.value_ids = False
                self.config_session_id.update_session_configuration_value(
                    vals=transformed_dict, product_tmpl_id=self.product_tmpl_id
                )
                self.env.cr.commit()
                values['qty_available'] = self.config_session_id.qty_available
                values['lot_ids'] = self.config_session_id.lot_ids

        return {"value": values, "domain": domain}
