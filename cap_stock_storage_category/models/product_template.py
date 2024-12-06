from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # velocity_id = fields.Many2one('stock.storage.velocity', string="Velocity")
    velocity_ids = fields.One2many('velocity.warehouse','product_tmpl_id', string="Velocity")

    #Todo: check calculation as well
    @api.model
    def _get_length_uom_id_from_ir_config_parameter(self):
        res = super()._get_length_uom_id_from_ir_config_parameter()
        if res == self.env.ref('uom.product_uom_foot'):
            res = self.env.ref('uom.product_uom_inch')
        return res