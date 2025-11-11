from odoo import models, fields


class EstatePropertyInheritedUsers(models.Model):
    _inherit = "res.users"

    properties = fields.One2many(
        "estate.property",
        "seller",
        domain="[('state','=','new'), ('state','=','offer_received')]",
    )
