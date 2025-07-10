from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    shipblu_zone_id = fields.Integer(
        string="ShipBlu Zone ID",
        help="ShipBlu Zone (required to create delivery orders)."
    )
