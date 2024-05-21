from odoo import models, fields, api, _
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging


_logger = logging.getLogger(__name__)



class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'


    sold_date = fields.Date('Sold Date')
    warranty_period = fields.Integer('Warranty Period')
    warranty_expired = fields.Boolean(compute='_compute_warranty_expired')

    @api.depends('sold_date', 'warranty_period')
    def _compute_warranty_expired(self):
        for record in self:
            if record.sold_date and record.warranty_period:
                _logger.warning(f"*******{record.sold_date} {record.warranty_period} {record.sold_date + relativedelta(days=record.warranty_period)} {fields.Date.today()}")
                record.warranty_expired = True if (record.sold_date + relativedelta(days=record.warranty_period)) < fields.Date.today() else False
            else:
                record.warranty_expired = False
