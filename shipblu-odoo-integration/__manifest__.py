{
    "name": "ShipBlu",
    "version": "18.0.1.0.0",
    "summary": "Connect your ShipBlu account to your Odoo apps and make shipping easier than ever!",
    "category": "Warehouse",
    "author": "ShipBlu",
    "license": "LGPL-3",
    "depends": ["base", "sale_management"],
    "data": [
        "security/ir.model.access.csv",
        "views/sale_order_views.xml",
        "views/res_partner_views.xml"
    ],
    "installable": True,
    "application": True,
        "images": ["static/description/icon.png"]
}
