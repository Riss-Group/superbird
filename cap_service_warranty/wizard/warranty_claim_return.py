
from odoo import api, fields, models
from odoo.fields import Command


class WarrantyClaimReturn(models.TransientModel):
    _name = 'warranty.claim.return'

    warranty_claim_id = fields.Many2one('warranty.claim', string="Warranty Claim")
    is_return = fields.Selection([('from_customer', 'From Customer'), ('to_supplier', 'To Supplier')],
                                 string="Is Return")
    picking_type_id = fields.Many2one('stock.picking.type', string="Picking Type")
    return_lines = fields.One2many('warranty.claim.return.line', 'warranty_claim_return_id', string="Return Lines")
    partner_id = fields.Many2one('res.partner', string="Partner")


    # @api.model
    # def default_get(self, fields):
    #     res = super().default_get(fields)
    #     res['warranty_claim_id'] = self.env.context.get('active_id')
    #     return res

    def action_create_return(self):
        self.ensure_one()
        return self._create_picking()

    def _create_picking(self):
        picking_id = self.env['stock.picking'].create({
            'picking_type_id': self.picking_type_id.id,
            'partner_id': self.partner_id.id,
            'warranty_claim_id': self.warranty_claim_id.id,
            'origin': self.warranty_claim_id.name,
            'move_ids': [Command.create(line._prepare_stock_move()) for line in self.return_lines]})


class WarrantyClaimReturnLine(models.TransientModel):
    _name = 'warranty.claim.return.line'

    warranty_claim_return_id = fields.Many2one('warranty.claim.return', string="Warranty Claim Return")
    product_id = fields.Many2one('product.product', string="Product")
    quantity = fields.Integer(string="Quantity")
    unit_price = fields.Float(string="Unit Price")
    warranty_claim_line_id = fields.Many2one('warranty.claim.line', string="Warranty Claim Line")

    def _prepare_stock_move(self):
        return {'name': self.product_id.name,
                'product_id': self.product_id.id,
                'product_uom_qty': self.quantity,
                'product_uom': self.product_id.uom_id.id,
                'location_id': self.warranty_claim_return_id.picking_type_id.default_location_src_id.id,
                'location_dest_id': self.warranty_claim_return_id.picking_type_id.default_location_dest_id.id,
                'warranty_claim_line_id': self.warranty_claim_line_id.id}

