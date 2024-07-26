from odoo import models, api, fields
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import test_python_expr


class ReorderingRulePythonCode(models.Model):
    _name = 'reordering.rule.python.code'
    _description = 'Reordering Rule Python Code'


    name = fields.Char()
    python_code = fields.Text(string='Python Code')


    @api.constrains('python_code')
    def _check_python_code(self):
        '''
            Validate the syntax of the Python code in the 'python_code' field.
            Raises a ValidationError if the syntax is incorrect (AKA Unsafe Execution from Base safe_eval).
        '''
        for record in self.sudo().filtered('python_code'):
            msg = test_python_expr(expr=record.python_code.strip(), mode="exec")
            if msg:
                raise ValidationError(msg)
