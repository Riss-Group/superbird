from odoo import models, fields


class BaseSubstateType(models.Model):
    _inherit = "base.substate.type"

    model = fields.Selection(
        selection_add=[("stock.picking", "Stock picking")], ondelete={"stock.picking": "cascade"})

class StockPicking(models.Model):
    _inherit = ['stock.picking', 'base.substate.mixin']
    _name = 'stock.picking'
