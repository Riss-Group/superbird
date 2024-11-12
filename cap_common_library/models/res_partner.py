from odoo import models, api, fields
from odoo.exceptions import ValidationError
from odoo.fields import Datetime
import logging
logger = logging.getLogger()

class ResPartner(models.Model):
    _inherit = 'res.partner'

    #CUSTOMER FIELDS
    is_customer = fields.Boolean()
    customer_class_id = fields.Many2one('res.partner.segmentation', string='Customer Class')
    bus_segmentation_id = fields.Many2one('res.partner.segmentation', string='Bus Segmentation')
    bus_customer_type_id = fields.Many2one('res.partner.type', string='Bus Customer Type')
    customer_level_id = fields.Many2one('res.partner.level', string='Customer Level')
    parts_territory_id = fields.Many2one('res.partner.territory', string='Parts Territory')
    bus_territory_id = fields.Many2one('res.partner.territory', string='Bus Territory')
    service_territory_id = fields.Many2one('res.partner.territory', string='Service Territory')
    parts_route_number = fields.Integer(string='Route Number')
    freight_term_id = fields.Many2one('res.partner.freight_term', string='Freight Terms')
    parts_salesperson_id = fields.Many2one('res.users', string='Parts Salesperson')
    bus_salesperson_id = fields.Many2one('res.users', string='Bus Salesperson')
    bus_salesperson_backup_id = fields.Many2one('res.users', string='Bus Salesperson (Backup)')
    special_constant_id = fields.Many2one('res.partner.constant', string='Special Constant')
    default_garage_id = fields.Many2one('service.garage', string='Default Garage')
    legacy_customer = fields.Char('Legacy Customer #', translate=True)
    second_legacy_customer = fields.Char('Second Legacy Customer #')
    can_sell_bus = fields.Boolean('Bus Orders Accepted')
    can_sell_parts = fields.Boolean('Parts Order Accepted')
    can_backorder = fields.Boolean('Accept BO')
    parts_required_po = fields.Boolean('PO Required Parts')
    bus_required_po = fields.Boolean('PO Required Bus')
    service_required_po = fields.Boolean('PO Required WO')
    fleet_gm = fields.Char('Fleet # GM', translate=True)
    fleet_ford = fields.Char('Fleet # Ford', translate=True)
    fleet_bb = fields.Char('Fleet # BB', translate=True)
    number_A = fields.Integer('No. Minibus')
    last_entered_A = fields.Datetime('No. Minibus last updated')
    number_C = fields.Integer('No. Conventional bus')
    last_entered_C = fields.Datetime('No. Conventional bus last updated')
    number_D = fields.Integer('No. Flat nose bus')
    last_entered_D = fields.Datetime('No. Flat nose last updated')
    number_MV = fields.Integer('No. Minivans')
    last_entered_MV = fields.Datetime('No. Minivans last updated')
    saaq = fields.Char('SAAQ file number', translate=True)
    bid_assist_phone = fields.Char('Bid Assist Phone')
    bb_primary_body_plan = fields.Char('BB Primary Body Plan', translate=True)
    operator = fields.Char('Operator ID')
    dot_inspector_id = fields.Many2one('res.partner.inspector', string='DOT Inspector')
#VENDOR FIELDS
    is_supplier = fields.Boolean()
    mid_number = fields.Char('MID Number', translate=True)
    account_number = fields.Char('Account Number', translate=True)
    min_order = fields.Float('Min Order Amount')
    free_ship_threshold = fields.Float('Free Ship Threshold')
    saving_threshold_ids = fields.One2many('res.partner.savings', 'partner_id', string='Saving Threshold Matrix')
    default_incoterm_id = fields.Many2one('account.incoterms', string='FOB')
    product_labeled = fields.Boolean('Product Labeled?')
    labels_supplied_by_us = fields.Boolean('Labels Supplied By Us?')
    direct_ship = fields.Boolean('Direct Ship?')
    communication_preference = fields.Selection([
        ('email', 'Email'),
        ('phone', 'Phone'),
        ('sms', 'SMS'),
        ('letter', 'Letter'),
    ], string="Emission PO")
    supplier_username = fields.Char('Supplier Website Username', translate=True)
    supplier_password = fields.Char('Supplier Website Password', translate=True)
    discount_web_order = fields.Float('Discount Web Order')
    special_instructions = fields.Char('Special Instructions', translate=True)
    pricelist_type = fields.Char('Pricelist Type', translate=True)
    pricelist_period = fields.Char('Pricelist Period', translate=True)
    allowed_order_day_ids = fields.Many2many('res.partner.available_day', string='Specific Order Day', relation='partner_order_day_rel')
    allowed_delivery_day_ids = fields.Many2many('res.partner.available_day', string='Specific Delivery Day', relation='partner_delivery_day_rel')
    booking_period_id = fields.Many2one('res.partner.booking', string='Booking Period')
    booking_notes = fields.Char('Booking Notes', translate=True)

    @api.model_create_multi
    def create(self, vals_list):
        now = Datetime.now()
        for vals in vals_list:
            if 'number_A' in vals:
                vals['last_entered_A'] = now
            if 'number_C' in vals:
                vals['last_entered_C'] = now
            if 'number_D' in vals:
                vals['last_entered_D'] = now
            if 'number_MV' in vals:
                vals['last_entered_MV'] = now
        return super().create(vals_list)

    def write(self, vals):
        now = Datetime.now()
        if 'number_A' in vals:
            vals['last_entered_A'] = now
        if 'number_C' in vals:
            vals['last_entered_C'] = now
        if 'number_D' in vals:
            vals['last_entered_D'] = now
        if 'number_MV' in vals:
            vals['last_entered_MV'] = now
        return super().write(vals)

class ResPartnerSegmentation(models.Model):
    _name = "res.partner.segmentation"
    _description = "Customer Segmentation"

    name = fields.Char('Name', translate=True)

class ResPartnerType(models.Model):
    _name = "res.partner.type"
    _description = "Customer Type"

    name = fields.Char('Name', translate=True)

class ResPartnerLevel(models.Model):
    _name = "res.partner.level"
    _description = "Customer Level"

    name = fields.Char('Name', translate=True)

class ResPartnerTerritory(models.Model):
    _name = "res.partner.territory"
    _description = "Customer Territory"

    name = fields.Char('Name', translate=True)
    
class ResPartnerFreightTerm(models.Model):
    _name = "res.partner.freight_term"
    _description = "Customer Freight Term"

    name = fields.Char('Name', translate=True)

class ResPartnerConstant(models.Model):
    _name = "res.partner.constant"
    _description = "Special Constant"

    name = fields.Char('Name', translate=True)

class ServiceGarage(models.Model):
    _name = "service.garage"
    _description = "Service Garage"

    name = fields.Char('Name', translate=True)

class ResPartnerInspector(models.Model):
    _name = "res.partner.inspector"
    _description = "DOT Inspector"

    name = fields.Char('Name', translate=True)

class ServiceGarage(models.Model):
    _name = "service.garage"
    _description = "Service Garage"

    name = fields.Char('Name', translate=True)

class ResPartnerAvailableDay(models.Model):
    _name = "res.partner.available_day"
    _description = "Available Day"

    name = fields.Char('Name', translate=True)
    
class ResPartnerBooking(models.Model):
    _name = "res.partner.booking"
    _description = "Booking Period"

    name = fields.Char('Name', translate=True)

class ResPartnerSavings(models.Model):
    _name = "res.partner.savings"
    _description = "Saving Threshold Matrix"

    name = fields.Char('Name')
    partner_id = fields.Many2one('res.partner', string='Partner')
    currency_id = fields.Many2one('res.currency', related='partner_id.currency_id')
    percent_discount = fields.Float(string="% Discount")
    currency_discount = fields.Monetary(string="$ Discount")
    trigger_threshold = fields.Monetary()
