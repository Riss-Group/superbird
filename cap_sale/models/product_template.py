from odoo import fields, api, models
import logging

_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def cap_get_products(self,):
        msg = "\n\nHI MOM\n\n"
        _logger.info(msg)

        return msg
