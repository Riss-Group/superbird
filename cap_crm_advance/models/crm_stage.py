from odoo import models, fields
from odoo.exceptions import UserError

class CRMStage(models.Model):
    _inherit = 'crm.stage'

    is_proposition = fields.Boolean(string="Is Proposition")

    def write(self, vals):
        if vals.get('is_proposition'):
            proposition_stage = self.env['crm.stage'].search([('is_proposition','=',True)],limit=1)
            if proposition_stage:
                raise UserError(f"""Only 1 stage can be configured as the Proposition Stage. If you would like to make the '{self.name}' the proposition stage then re-configure the '{proposition_stage.name}' stage.""")
        return super(CRMStage, self).write(vals)
