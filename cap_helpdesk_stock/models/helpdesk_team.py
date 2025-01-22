# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HelpdeskTeam(models.Model):
    _inherit = 'helpdesk.team'

    default_return_operation_type = fields.Many2one('stock.picking.type', domain="[('code','=', 'incoming')]", store=True,
                                                    help="If none selected then the system will use the return operation of the picking")
    sequence_id = fields.Many2one(
        'ir.sequence', 'Reference Sequence',
        check_company=True, copy=False)
    sequence_code = fields.Char('Sequence Prefix', required=True, copy=False)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('sequence_id') and vals.get('sequence_code'):
                    vals['sequence_id'] = self.env['ir.sequence'].sudo().create({
                    'name': _('Sequence') + ' ' + vals['sequence_code'],
                    'prefix': vals['sequence_code'], 'padding': 5,
                    'company_id': vals.get('company_id') or self.env.company.id,
                }).id
        return super(HelpdeskTeam, self).create(vals_list)

    def write(self, vals):
        if 'sequence_code' in vals:
            for team in self:
                if team.sequence_id:
                    team.sequence_id.sudo().write({
                        'name': _('Sequence') + ' ' + vals['sequence_code'],
                        'prefix': vals['sequence_code'], 'padding': 5,
                        'company_id': team.env.company.id,
                    })
                else:
                    vals['sequence_id'] = self.env['ir.sequence'].sudo().create({
                        'name': _('Sequence') + ' ' + vals['sequence_code'],
                        'prefix': vals['sequence_code'], 'padding': 5,
                        'company_id': vals.get('company_id') or self.env.company.id,
                    }).id

        return super(HelpdeskTeam, self).write(vals)