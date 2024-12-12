# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    ai_prompt = fields.Text(related="company_id.ai_prompt", readonly=False)
    ai_model_ids = fields.Many2many(related="company_id.ai_model_ids", readonly=False)