from odoo import  models, fields, api
from odoo.exceptions import UserError


class ServiceOrderTemplate(models.Model):
    _name = 'service.template'   
    _description = 'Service Templates'


    ttype = fields.Many2one('service.template.type', string="Type")
    name = fields.Text(string="Op Code")
    cause = fields.Text()
    correction = fields.Text(string='Fix')
    project_id = fields.Many2one('project.project', string='Department')
    service_template_parts = fields.One2many('service.template.parts', 'service_template_id')
    service_template_service = fields.One2many('service.template.service', 'service_template_id')


class ServiceOrderTemplateParts(models.Model):
    _name = 'service.template.parts'   
    _description = 'Service Template Parts'


    service_template_id = fields.Many2one('service.template')
    product_id = fields.Many2one('product.product', domain=[('detailed_type','!=','service')])
    quantity = fields.Float()
    est_list_price = fields.Float(related='product_id.lst_price')
    est_subtotal = fields.Float(compute='_compute_subtotal', group_operator='sum')

    @api.depends('est_list_price','quantity')
    def _compute_subtotal(self):
        for record in self:
            record.est_subtotal = record.est_list_price * record.quantity


class ServiceOrderTemplateParts(models.Model):
    _name = 'service.template.service'   
    _description = 'Service Template service'


    service_template_id = fields.Many2one('service.template')
    product_id = fields.Many2one('product.product', domain=[('detailed_type','=','service')])
    quantity = fields.Float()
    est_list_price = fields.Float(related='product_id.lst_price')
    est_subtotal = fields.Float(compute='_compute_subtotal', group_operator='sum')

    @api.depends('est_list_price','quantity')
    def _compute_subtotal(self):
        for record in self:
            record.est_subtotal = record.est_list_price * record.quantity

class ServiceOrderTemplate(models.Model):
    _name = 'service.template.type'   
    _description = 'Service Templates'

    name = fields.Text(string="Type")