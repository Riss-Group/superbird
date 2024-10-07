from odoo import  models, fields, api
from odoo.exceptions import UserError


class ServiceOrderTemplate(models.Model):
    _name = 'service.ccc'   
    _description = 'Service Templates'


    name = fields.Text()
    cause = fields.Text()
    correction = fields.Text(string='Fix')
    project_id = fields.Many2one('project.project', string='Department')
    service_template_parts = fields.One2many('service.ccc.parts', 'service_template_id')
    service_template_service = fields.One2many('service.ccc.service', 'service_template_id')


class ServiceOrderTemplateParts(models.Model):
    _name = 'service.ccc.parts'   
    _description = 'Service Template Parts'


    service_template_id = fields.Many2one('service.ccc')
    product_id = fields.Many2one('product.product', domain=[('detailed_type','!=','service')])
    quantity = fields.Float()


class ServiceOrderTemplateParts(models.Model):
    _name = 'service.ccc.service'   
    _description = 'Service Template service'


    service_template_id = fields.Many2one('service.ccc')
    product_id = fields.Many2one('product.product', domain=[('detailed_type','=','service')])
    quantity = fields.Float()