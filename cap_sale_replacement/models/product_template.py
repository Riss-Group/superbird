from odoo import models, fields, api, _

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    replacement_id = fields.Many2one(
        'product.product',
        string='Replacement',
        compute='_compute_replacement_id',
        inverse='_set_replacement',
        store=True
    )

    @api.depends('product_variant_ids.replacement_id')
    def _compute_replacement_id(self):
        for template in self:
            template.replacement_id = False
            variants = template.product_variant_ids
            if variants:
                template.replacement_id = variants[-1].replacement_id

    def _set_replacement(self):
        for template in self:
            variants = template.product_variant_ids
            if variants:
                variants.replacement_id = template.replacement_id
