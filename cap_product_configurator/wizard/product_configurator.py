from odoo import _, api, fields, models, tools
from collections import defaultdict

from odoo.exceptions import UserError


class ProductConfigurator(models.TransientModel):
    _inherit = "product.configurator"

    qty_available = fields.Float(
        'Quantity On Hand', digits='Product Unit of Measure')
    product_ids = fields.Many2many('product.product')

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

    def apply_onchange_values(self, values, field_name, field_onchange):
        """Called from web-controller
        - original onchage return M2o values in formate
        (attr-value.id, attr-value.name) but on website
        we need only attr-value.id"""
        product_tmpl_id = self.env["product.template"].browse(
            values.get("product_tmpl_id", [])
        )
        if not product_tmpl_id:
            product_tmpl_id = self.product_tmpl_id
        field_name.append('qty_available')
        qty_available = product_tmpl_id.qty_available if product_tmpl_id else 0

        config_session_id = self.env["product.config.session"].browse(
            values.get("config_session_id", [])
        )
        if not config_session_id:
            config_session_id = self.config_session_id

        state = values.get("state", False)
        if not state:
            state = self.state

        cfg_vals = self.env["product.attribute.value"]
        if values.get("value_ids", []):
            cfg_vals = self.env["product.attribute.value"].browse(
                values.get("value_ids", [])[0][2]
            )
        if not cfg_vals:
            cfg_vals = self.value_ids

        field_prefix = self._prefixes.get("field_prefix")


        view_val_ids = set()
        view_attribute_ids = set()

        try:
            cfg_step_id = int(state)
            cfg_step = product_tmpl_id.config_step_line_ids.filtered(
                lambda x: x.id == cfg_step_id
            )
        except Exception:
            cfg_step = self.env["product.config.step.line"]

        dynamic_fields = {k: v for k, v in values.items() if k.startswith(field_prefix)}

        # Get the unstored values from the client view
        for k, v in dynamic_fields.items():
            attr_id = int(k.split(field_prefix)[1])
            valve_ids = self.env["product.attribute.value"]
            if isinstance(v, list):
                for att in v:
                    valve_ids |= product_tmpl_id.config_line_ids.filtered(
                        lambda line: int(att[1])
                                     in line.domain_id.domain_line_ids.value_ids.ids
                    ).mapped("value_ids")
            else:
                valve_ids = product_tmpl_id.config_line_ids.filtered(
                    lambda line: int(v) in line.domain_id.domain_line_ids.value_ids.ids
                ).mapped("value_ids")

            self.domain_attr_2_ids = [(6, 0, valve_ids.ids)]

            line_attributes = cfg_step.attribute_line_ids.mapped("attribute_id")
            if not cfg_step or attr_id in line_attributes.ids:
                view_attribute_ids.add(attr_id)
            else:
                continue
            if not v:
                continue
            if isinstance(v, list):
                for a in v:
                    view_val_ids.add(a[1])
            elif isinstance(v, int):
                view_val_ids.add(v)

        # Clear all DB values belonging to attributes changed in the wizard
        cfg_vals = cfg_vals.filtered(
            lambda v: v.attribute_id.id not in view_attribute_ids
        )
        # Combine database values with wizard values_available
        cfg_val_ids = cfg_vals.ids + list(view_val_ids)

        domains = self.get_onchange_domains(
            values, cfg_val_ids, product_tmpl_id, config_session_id
        )
        if domains:
            for key, value in domains.items():
                if [key] == field_name:
                    if len(domains) == 1:
                        self.dyn_field_value = key
                        self.domain_attr_ids = [(6, 0, value[0][2])]
                    else:
                        self.dyn_field_2_value = key
                        self.domain_attr_2_ids = [(6, 0, value[0][2])]

                    continue
                elif values and value[0][2]:
                    self.dyn_field_2_value = key
                    self.domain_attr_2_ids = [(6, 0, value[0][2])]

        vals = self.get_form_vals(
            dynamic_fields=dynamic_fields,
            domains=domains,
            product_tmpl_id=product_tmpl_id,
            config_session_id=config_session_id,
        )
        if cfg_val_ids :
            template_values = self.env['product.template.attribute.value'].search([('product_tmpl_id','=',product_tmpl_id.id),('attribute_id','in',list(view_attribute_ids)),('product_attribute_value_id','in',cfg_val_ids)])
            qty_available = self._get_product_ids_qty_available(template_values.ids)

        vals['qty_available'] = qty_available
        return {"value": vals, "domain": domains}

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
