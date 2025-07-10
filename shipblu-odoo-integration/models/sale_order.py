from odoo import models, fields, api, _
from odoo.exceptions import UserError

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
        self.ensure_one()

        if not self.partner_shipping_id:
            raise UserError(_("Shipping address is required."))
        if not self.partner_shipping_id.shipblu_zone_id:
            raise UserError(_("Shipping address must have a ShipBlu Zone ID."))
        if not self.shipblu_package_size or self.shipblu_package_size < 1:
            raise UserError(_("Please set a valid ShipBlu package size (1-5)."))

        # Find the ShipBlu External Service connection
        connection = self.env['ir.external.service'].search([('name', '=', 'ShipBlu')], limit=1)
        if not connection:
            raise UserError(_("No ShipBlu connection found. Please set it up in Settings → External Services."))

        # Build ShipBlu payload
        payload = {
            "customer": {
                "full_name": self.partner_shipping_id.name,
                "email": self.partner_shipping_id.email or "",
                "phone": self.partner_shipping_id.phone or "",
                "address": {
                    "line_1": self.partner_shipping_id.street or "",
                    "line_2": self.partner_shipping_id.street2 or "",
                    "zone": self.partner_shipping_id.shipblu_zone_id
                }
            },
            "packages": [
                {
                    "package_size": self.shipblu_package_size
                }
            ]
        }

        # Make the call via Odoo's external service
        try:
            result = connection.call(
                '/delivery-orders/',
                method='POST',
                json=payload
            )
        except Exception as e:
            raise UserError(_("Error communicating with ShipBlu: %s") % str(e))

        tracking_number = result.get("tracking_number")
        shipment_status = result.get("status")

        if not tracking_number:
            raise UserError(_("Invalid response from ShipBlu: no tracking number."))

        self.write({
            "shipblu_tracking_number": tracking_number,
            "shipblu_shipment_status": shipment_status,
        })

        self.message_post(body=_("ShipBlu delivery order created. Tracking Number: %s" % tracking_number))
