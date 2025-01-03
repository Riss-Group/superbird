from odoo import models, fields, api
from odoo.exceptions import UserError


class ProductProduct(models.Model):
    _inherit = 'product.product'
    

    create_fleet_vehicle = fields.Boolean(related='product_tmpl_id.create_fleet_vehicle', readonly=True, store=True, string="Create Fleet Vehicle")
    vehicle_year = fields.Selection(related='product_tmpl_id.vehicle_year', readonly=True, store=True, string="Year")
    vehicle_make_id = fields.Many2one('fleet.vehicle.model.brand', related='product_tmpl_id.vehicle_make_id', readonly=True, store=True, string="Make")
    vehicle_model_id = fields.Many2one('fleet.vehicle.model', related='product_tmpl_id.vehicle_model_id', readonly=True, store=True, string="Model")
    available_vehicle_model_ids = fields.Many2many('fleet.vehicle.model', related='product_tmpl_id.available_vehicle_model_ids', compute='_compute_available_vehicle_model_ids')
    sequence_code = fields.Char(store=True, compute="_compute_sequence_code")
    sequence_prefix = fields.Char(related="sequence_id.prefix", store=True)
    sequence_id = fields.Many2one('ir.sequence', compute="_compute_sequence_code", store=True, string="Sequence", readonly=True)

    @api.depends('vehicle_year', 'product_template_attribute_value_ids')
    def _compute_sequence_code(self):
        for record in self:
            pav_bu = record.product_template_attribute_value_ids.filtered(lambda x: x.attribute_id.is_bu)
            pav_cap = record.product_template_attribute_value_ids.filtered(lambda x: x.attribute_id.is_cap)
            if record.vehicle_year and pav_bu and pav_cap:
                sequence_prefix = f"({pav_bu[0].company_code}) {record.vehicle_year[-2:]}-{pav_cap[0].name}"
                sequence_code = f"{pav_bu[0].name}_{record.vehicle_year[-2:]}_{pav_cap[0].name}"
                record.sequence_code = sequence_code
                sequence_id = self.env['ir.sequence'].sudo().search([('code', '=', sequence_code)], limit=1)
                if not sequence_id:
                    sequence_id = self.env['ir.sequence'].sudo().create({
                        'name': f"Stock Number: {sequence_code}",
                        'code': sequence_code,
                        'implementation': 'no_gap',
                        'prefix': sequence_prefix,
                        'padding': 4,
                        'company_id':False
                    })
                record.sequence_id = sequence_id