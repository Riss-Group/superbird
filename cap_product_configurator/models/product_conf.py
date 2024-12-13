import logging
from odoo import _, api, fields, models


_logger = logging.getLogger(__name__)


def get_last_list(nested):
    if type(nested).__name__ == 'dict_values':
        return get_last_list(list(nested))

    elif isinstance(nested, list):
        return get_last_list(nested[-1])

    elif isinstance(nested, int):
        return nested

def filter_integers(input_dict):
    return {key: value for key, value in input_dict.items() if isinstance(value, int)}


class ProductConfigSession(models.Model):
    _inherit = "product.config.session"


    qty_available = fields.Float(
        'Quantity On Hand', digits='Product Unit of Measure', compute="_compute_qty_available")
    lot_ids = fields.Html(compute="_compute_qty_available")


    @api.depends('product_tmpl_id','value_ids')
    def _compute_qty_available(self):
        for config in self:
            config.lot_ids = ''

            product_ids = self.env['product.product'].search([('product_tmpl_id', '=', config.product_tmpl_id.id)])
            qty_available =  0

            template_values = self.env['product.template.attribute.value'].search([('product_tmpl_id','=', config.product_tmpl_id.id),('attribute_id','in',config.value_ids.mapped('attribute_id.id')),('product_attribute_value_id','in', config.value_ids.ids)])
            available_products = product_ids.filtered(lambda x: all(value_id.id in product_ids.product_template_variant_value_ids.ids for value_id in template_values))

            for product in available_products :
                if config.value_ids :
                    qty_available += product.qty_available
                    quants = self.env['stock.quant'].search([('product_id', 'in', available_products.ids),('on_hand','=', True)])
                    if quants :
                        config.lot_ids = self.generate_lot_table(quants)

            config.qty_available = qty_available


    def generate_lot_table(self, lot_data):
        table_html = """
        <style>
            .table th, .table td {
                padding: 10px;  /* Add padding for better readability */
            }
            .table th {
                width: 200px;  /* Set width for the headers */
            }
            .table td {
                width: 250px;  /* Set width for the table data */
            }
        </style>
        <table class="table table-striped">
            <thead>
                <tr>
                    <th>Serial(s)</th>
                    <th>Location</th>
                </tr>
            </thead>
            <tbody>
        """

        for line in lot_data:
            table_html += f"""
            <tr>
                <td>{line.lot_id.name}</td>
                <td>{line.location_id.display_name}</td>
            </tr>
            """

        table_html += "</tbody></table>"

        return table_html

