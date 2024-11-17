from odoo import models, fields, api


class BaseModel(models.AbstractModel):
    _inherit = 'base'


    def get_selection_label(self, object, field_name, field_value):
        '''
            This method allows us to get the label value for the selection field
        '''
        if field_value:
            return (dict(self.env[object].fields_get(allfields=[field_name])[field_name]['selection'])[field_value])
        else:
            return False
