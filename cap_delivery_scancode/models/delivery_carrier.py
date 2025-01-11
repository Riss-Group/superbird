# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from .scancode_request import ScancodeRequest

class DeliverCarrier(models.Model):
    _inherit = 'delivery.carrier'

    delivery_type = fields.Selection(selection_add=[('scancode', 'ScanCode')],
                                     ondelete={'scancode': lambda recs: recs.write({'delivery_type': 'fixed', 'fixed_price': 0})})
    scancode_user_id = fields.Char("Scancode User ID", groups="base.group_system")
    scancode_password = fields.Char("Scancode Password", groups="base.group_system")
    scancode_api_url = fields.Char("Scancode API URL", groups="base.group_system")
    carrier_code = fields.Char('ScanCode Carrier Code', index=True)
    service_code = fields.Char('ScanCode Service Code', index=True)

    def scancode_rate_shipment(self, order):
        """Request rates for a shipment."""
        if not (self.scancode_user_id and self.scancode_password and self.scancode_api_url):
            raise UserError("ScanCode API credentials are missing.")

        scancode_request = ScancodeRequest(user_id=self.scancode_user_id,
                                           password=self.scancode_password,
                                           api_url=self.scancode_api_url,
                                           debug_logger=self.log_xml)

        request_xml = f"""<?xml version="1.0"?>
        <RateEngineRequest>
            <UserCredentials>
                <UserID>{self.scancode_user_id}</UserID>
                <UserPassword>{self.scancode_password}</UserPassword>
            </UserCredentials>
            <ShipmentRateRequest>
                <SONum>{order.name}</SONum>
                <DestPostal>{order.partner_shipping_id.zip}</DestPostal>
                <DestProvince>{order.partner_shipping_id.state_id.code}</DestProvince>
                <DestCountry>{order.partner_shipping_id.country_id.code}</DestCountry>
                <Weight>{sum(line.product_id.weight * line.product_uom_qty for line in order.order_line)}</Weight>
                <Pieces>{len(order.order_line)}</Pieces>
                <Carrier>{self.carrier_code}</Carrier>
                <Service>{self.service_code}</Service>
                <NumRatesReturn>1</NumRatesReturn>
                <ShipperPostal>J2E 0A1</ShipperPostal>
                <Branch></Branch>
            </ShipmentRateRequest>
        </RateEngineRequest>"""

        response = scancode_request._make_api_request("RateEngineRequest", data=request_xml)
        rates = []
        print("response : ",response)
        for rate in response.findall('.//ShipmentRateDetails'):
            print("rate : ",rate)
            carrier = rate.find('Carrier').text
            service = rate.find('ServiceDescription').text
            cost = rate.find('RateTotal').text
            rates.append({'carrier': carrier, 'service': service, 'price': cost, 'success': True})
        print("rates : ",rates)
        if not rates:
            rates.append({'success': False, 'price': 0.0, 'error_message': response.find('.//ShipmentRateError').find('.//ErrorDetails').text})
        return rates[0]

#     < PieceRateRequest >
#     < PieceID > 1 < / PieceID >
#     < PieceWeight > 10 < / PieceWeight >
# < / PieceRateRequest >

    def scancode_send_shipping(self, pickings):
        """Send a shipment via scancode."""
        if not (self.scancode_user_id and self.scancode_password and self.scancode_api_url):
            raise UserError("Scancode API credentials are missing.")

        scancode_request = ScancodeRequest(user_id=self.scancode_user_id,
                                             password=self.scancode_password,
                                             debug_logger=self.env['ir.logging']._log)

        for picking in pickings:
            request_xml = f"""<?xml version="1.0"?>
            <ShippingAPIRequest>
                <UserCredentials>
                    <UserID>{self.scancode_user_id}</UserID>
                    <UserPassword>{self.scancode_password}</UserPassword>
                </UserCredentials>
                <AddPackage>
                    <SONum>{picking.name}</SONum>
                    <ShipperPostal>{picking.picking_type_id.warehouse_id.partner_id.zip}</ShipperPostal>
                    <ShipperProvince>{picking.picking_type_id.warehouse_id.partner_id.state_id.code}</ShipperProvince>
                    <ShipperCountry>{picking.picking_type_id.warehouse_id.partner_id.country_id.code}</ShipperCountry>
                    <DestPostal>{picking.partner_id.zip}</DestPostal>
                    <DestProvince>{picking.partner_id.state_id.code}</DestProvince>
                    <DestCountry>{picking.partner_id.country_id.code}</DestCountry>
                    <Weight>{sum(line.product_id.weight * line.quantity_done for line in picking.move_line_ids)}</Weight>
                    <Pieces>{len(picking.move_line_ids)}</Pieces>
                    <OkToShip>Y</OkToShip>
                </AddPackage>
            </ShippingAPIRequest>"""

            response = False
            # response = scancode_request._make_api_request("ShippingAPIRequest", data=request_xml)
            status = response.find('.//Status').text
            if status != 'OK':
                error_details = response.find('.//ErrorDetails').text
                raise UserError(f"Error in shipping: {error_details}")

            # Add tracking numbers
            tracking_numbers = []
            for piece in response.findall('.//PieceTrackNo'):
                tracking_numbers.append(piece.find('TrackingNo').text)
            picking.write({'carrier_tracking_ref': ', '.join(tracking_numbers)})
        return True
