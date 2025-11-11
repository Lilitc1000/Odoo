from odoo import models
from odoo.orm.commands import Command


class EstateProperty(models.Model):
    _inherit = "estate.property"

    def action_sold_property(self):
        for property in self:
            selling_price = property.selling_price
            administrative_fee = 100.00
            _ = self.env["account.move"].create(
                {
                    "partner_id": property.buyer.id,
                    "move_type": "out_invoice",
                    "invoice_line_ids": [
                        Command.create(
                            {
                                "name": "Property Sale (6% of selling price)",
                                "quantity": 1,
                                "price_unit": selling_price * 0.06,
                            },
                        ),
                        Command.create(
                            {
                                "name": "Administrative Fees",
                                "quantity": 1,
                                "price_unit": administrative_fee,
                            },
                        ),
                    ],
                }
            )
        return super(EstateProperty, self).action_sold_property()