# -*- coding: utf-8 -*-

from odoo import models, fields, api

class vendorCoreReturn(models.Model):
    _name = 'core.return'
    _inherit = ['mail.thread.main.attachment', 'mail.activity.mixin']


    @api.model
    def default_get(self, fields):
        res = super(vendorCoreReturn, self).default_get(fields)
        res.update({'name': '/'})
        return res

    name = fields.Char(string="Name")
    partner_id = fields.Many2one('res.partner', string="Vendor", required=True)
    picking_ids = fields.Many2many('stock.picking', string="Picking")
    picking_count = fields.Integer('Picking Count', compute="_compute_picking_count")
    date = fields.Date('Date', default=fields.Date.today())

    @api.depends('picking_ids')
    def _compute_picking_count(self):
        for rec in self:
            rec.picking_count = len(rec.picking_ids)

    @api.model_create_multi
    def create(self, vals_list):
        result = super(vendorCoreReturn, self).create(vals_list)
        for rec in result:
            sequence = self.env['ir.sequence'].next_by_code('core.return')
            if rec.name == '/' and sequence:
                rec.name = sequence
        return result

    def action_open_dirty_cores_return(self):
        action =  {
            'name': 'Dirty Cores Return',
            'type': 'ir.actions.act_window',
            'res_model': 'dirty_core.return',
            'view_mode': 'form',
            'context': {
                'default_model': 'purchase.order',
                'default_partner_id': self.partner_id.id,
                'default_core_return_id': self.id,
            },
            'target': 'new',
        }
        return action

    def action_open_picking(self):
        action =  {
            'name': 'Stock Picking',
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'view_mode': 'tree,form',
            'domain': [('id','in', self.picking_ids.ids)],
            'context': {
                'create': False,
            },
        }
        return action