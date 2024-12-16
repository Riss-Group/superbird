
from odoo import api, fields, models


class Warehouse(models.Model):
    _inherit = "stock.warehouse"

    assign_user_ids = fields.Many2many('res.users', 'res_user_warehouse_rel', 'warehouse_id', 'user_id',
                                       string="Assigned Users",
                                       domain=lambda self: [
                                           ('groups_id', 'in', self.env.ref('stock.group_stock_user').id)])