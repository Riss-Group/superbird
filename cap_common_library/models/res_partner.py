from odoo import models, api, fields
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'

#CUSTOMER FIELDS
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
    legacy_customer = fields.Char('Legacy Customer #')
    second_legacy_customer = fields.Char('Second Legacy Customer #')
    can_sell_bus = fields.Boolean('Bus Orders Accepted')
    can_sell_parts = fields.Boolean('Parts Order Accepted')
    can_backorder = fields.Boolean('Accept BO')
    parts_required_po = fields.Boolean('PO Required Parts')
    bus_required_po = fields.Boolean('PO Required Bus')
    service_required_po = fields.Boolean('PO Required WO')
    fleet_gm = fields.Char('Fleet # GM')
    fleet_ford = fields.Char('Fleet # Ford')
    fleet_bb = fields.Char('Fleet # BB')
    number_A = fields.Integer('No. Minibus')
    last_entered_A = fields.Datetime('No. Minibus last updated')
    number_C = fields.Integer('No. Conventional bus')
    last_entered_C = fields.Datetime('No. Conventional bus last updated')
    number_D = fields.Integer('No. Flat nose bus')
    last_entered_D = fields.Datetime('No. Flat nose last updated')
    number_MV = fields.Integer('No. Minivans')
    last_entered_MV = fields.Datetime('No. Minivans last updated')
    saaq = fields.Char('SAAQ file number')
    bid_assist_phone = fields.Char('Bid Assist Phone')
    bb_primary_body_plan = fields.Char('BB Primary Body Plan')
    operator = fields.Char('Operator ID')
    dot_inspector_id = fields.Many2one('res.partner.inspector', string='DOT Inspector')
#VENDOR FIELDS
    mid_number = fields.Char('MID Number')
    account_number = fields.Char('Account Number')
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
    supplier_username = fields.Char('Supplier Website Username')
    supplier_password = fields.Char('Supplier Website Password')
    discount_web_order = fields.Float('Discount Web Order')
    special_instructions = fields.Char('Special Instructions')
    pricelist_type = fields.Char('Pricelist Type')
    pricelist_period = fields.Char('Pricelist Period')
    allowed_order_day_ids = fields.Many2many('res.partner.available_day', string='Specific Order Day', relation='partner_order_day_rel')
    allowed_delivery_day_ids = fields.Many2many('res.partner.available_day', string='Specific Delivery Day', relation='partner_delivery_day_rel')
    booking_period_id = fields.Many2one('res.partner.booking', string='Booking Period')
    booking_notes = fields.Char('Booking Notes')

class ResPartnerSegmentation(models.Model):
    _name = "res.partner.segmentation"
    _description = "Customer Segmentation"

    name = fields.Char('Name')

class ResPartnerType(models.Model):
    _name = "res.partner.type"
    _description = "Customer Type"

    name = fields.Char('Name')

class ResPartnerLevel(models.Model):
    _name = "res.partner.level"
    _description = "Customer Level"

    name = fields.Char('Name')

class ResPartnerTerritory(models.Model):
    _name = "res.partner.territory"
    _description = "Customer Territory"

    name = fields.Char('Name')
    
class ResPartnerFreightTerm(models.Model):
    _name = "res.partner.freight_term"
    _description = "Customer Freight Term"

    name = fields.Char('Name')

class ResPartnerConstant(models.Model):
    _name = "res.partner.constant"
    _description = "Special Constant"

    name = fields.Char('Name')

class ServiceGarage(models.Model):
    _name = "service.garage"
    _description = "Service Garage"

    name = fields.Char('Name')

class ResPartnerInspector(models.Model):
    _name = "res.partner.inspector"
    _description = "DOT Inspector"

    name = fields.Char('Name')

class ServiceGarage(models.Model):
    _name = "service.garage"
    _description = "Service Garage"

    name = fields.Char('Name')

class ResPartnerAvailableDay(models.Model):
    _name = "res.partner.available_day"
    _description = "Available Day"

    name = fields.Char('Name')
    
class ResPartnerBooking(models.Model):
    _name = "res.partner.booking"
    _description = "Booking Period"

    name = fields.Char('Name')

class ResPartnerSavings(models.Model):
    _name = "res.partner.savings"
    _description = "Saving Threshold Matrix"

    name = fields.Char('Name')
    partner_id = fields.Many2one('res.partner', string='Partner')
