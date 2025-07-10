from odoo import models, fields, api, _
from odoo.exceptions import UserError
import requests

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    shipblu_tracking_number = fields.Char(readonly=True, copy=False)
    shipblu_shipment_status = fields.Char(readonly=True, copy=False)
    shipblu_package_size = fields.Integer(
        string="ShipBlu Package Size",
        default=1,
        help="Package size for ShipBlu (1-5)"
    )

    def action_create_shipblu_delivery_order(self):
        for order in self:
            if not order.partner_shipping_id:
                raise UserError(_("Shipping address is required."))
            if not order.partner_shipping_id.shipblu_zone_id:
                raise UserError(_("Shipping address must have a ShipBlu Zone ID."))
            if not order.shipblu_package_size or order.shipblu_package_size < 1:
                raise UserError(_("Please set a valid ShipBlu package size (1-5)."))

            payload = {
                "customer": {
                    "full_name": order.partner_shipping_id.name,
                    "email": order.partner_shipping_id.email or "",
                    "phone": order.partner_shipping_id.phone or "",
                    "address": {
                        "line_1": order.partner_shipping_id.street or "",
                        "line_2": order.partner_shipping_id.street2 or "",
                        "zone": order.partner_shipping_id.shipblu_zone_id
                    }
                },
                "packages": [
                    {
                        "package_size": order.shipblu_package_size
                    }
                ]
            }

            api_key = self.env["ir.config_parameter"].sudo().get_param("shipblu.api_key")
            if not api_key:
                raise UserError(_("ShipBlu API Key is not configured. Please set 'shipblu.api_key' in System Parameters."))

            url = "https://api.shipblu.com/v1/delivery-orders/"
            headers = {
                "Authorization": f"Token {api_key}",
                "Content-Type": "application/json",
            }

            try:
                response = requests.post(url, json=payload, headers=headers, timeout=20)
            except requests.RequestException as e:
                raise UserError(_("Error connecting to ShipBlu: %s") % str(e))

            if response.status_code not in (200, 201):
                raise UserError(_("ShipBlu API Error: %s") % response.text)

            result = response.json()
            tracking_number = result.get("tracking_number")
            shipment_status = result.get("status")

            if not tracking_number:
                raise UserError(_("Invalid ShipBlu response: missing tracking number."))

            order.write({
                "shipblu_tracking_number": tracking_number,
                "shipblu_shipment_status": shipment_status,
            })

            order.message_post(body=_("ShipBlu delivery order created. Tracking Number: %s" % tracking_number))
