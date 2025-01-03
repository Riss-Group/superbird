from odoo import models, fields, api

class VelocityWarehouse(models.Model):
    _name = 'velocity.warehouse'

    velocity_id = fields.Many2one('stock.storage.velocity', string="Velocity")
    warehouse_id = fields.Many2one('stock.warehouse', string="Warehouse")
    product_tmpl_id = fields.Many2one('product.template', string="Product")

