from odoo import models, fields, api
from odoo.exceptions import UserError

class CRMStage(models.Model):
    _inherit = 'crm.stage'

    is_proposition = fields.Boolean(string="Is Proposition")
    is_lost = fields.Boolean('Is Lost Stage?')

    @api.constrains('is_proposition', 'is_lost')
    def _check_customer_reference_unique(self):
        for stage in self:
            if stage.is_proposition:
                duplicate_stages = self.search([('is_proposition', '=', True), ('id', '!=', stage.id)], limit=1)
                if duplicate_stages:
                    raise UserError(f"""Only 1 stage can be configured as the Proposition Stage. If you would like to make the '{stage.name}' the proposition stage then re-configure the '{duplicate_stages.name}' stage.""")
            if stage.is_lost:
                duplicate_lost_stages = self.search([('is_lost', '=', True), ('id', '!=', stage.id)], limit=1)
                if duplicate_lost_stages:
                    raise UserError(
                        f"""Only 1 stage can be configured as the Lost Stage. If you would like to make the '{stage.name}' the lost stage then re-configure the '{duplicate_lost_stages.name}' stage.""")
