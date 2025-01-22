from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_tradein_start(self):
        """Return action to start configuration wizard"""
        configurator_obj = self.env["product.configurator.sale"]
        ctx = dict(
            self.env.context,
            default_order_id=self.id,
            negative=True,
            wizard_model="product.configurator.sale",
            allow_preset_selection=True,
        )
        return configurator_obj.with_context(**ctx).get_wizard_action()
