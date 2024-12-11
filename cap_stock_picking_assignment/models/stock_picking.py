from odoo import  fields, models, api


class PickingType(models.Model):
    _inherit = "stock.picking.type"

    assign_user_ids = fields.Many2many('res.users', 'res_user_picking_type_rel', 'picking_type_id', 'user_id',
                                       string="Assigned Users",
                                       domain=lambda self: [('groups_id', 'in', self.env.ref('stock.group_stock_user').id)])



class Picking(models.Model):
    _inherit = "stock.picking"

    user_id = fields.Many2one('res.users', 'Responsible', tracking=True,
                              domain=lambda self: [('groups_id', 'in', self.env.ref('stock.group_stock_user').id)],
                              compute="_compute_user_id", store=True, default=False)

    @api.depends('state')
    def _compute_user_id(self):
        for record in self:
            if record.state == 'assigned' and not record.user_id:
                if record.picking_type_id.assign_user_ids:
                    record.user_id = record.get_user_id(record.picking_type_id.assign_user_ids)

    def get_user_id(self, users_can_be_assigned):
        picking_ids = self.search([('user_id', 'in', users_can_be_assigned.ids),
                                   ('state', '=', 'assigned'), ('picking_type_id', '=', self.picking_type_id.id)])
        max_assigned_picking = 0
        assign_user_id = self.env['res.users']
        for user in users_can_be_assigned:
            current_user_picking_ids = picking_ids.filtered(lambda p: p.user_id == user)
            if not assign_user_id:
                assign_user_id = user
                max_assigned_picking = len(current_user_picking_ids)
            elif len(current_user_picking_ids) < max_assigned_picking:
                max_assigned_picking = len(current_user_picking_ids)
                assign_user_id = user
        return assign_user_id
