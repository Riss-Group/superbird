# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    @api.model
    def default_get(self, fields):
        res = super(HelpdeskTicket, self).default_get(fields)
        res.update({'name': '/'})
        return res


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            team = self.env['helpdesk.team'].browse(vals.get('team_id'))
            if vals.get('name') == '/':
                if team.sequence_id:
                    vals['name'] = team.sequence_id.next_by_id()

        tickets = super().create(vals_list)
        return tickets


