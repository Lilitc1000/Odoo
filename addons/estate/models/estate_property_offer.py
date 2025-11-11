from odoo import fields, models, api
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Estate Offer Model"
    _order = "offer_price desc"

    offer_price = fields.Float(string="Offer Price")
    status = fields.Selection(
        [("accepted", "Accepted"), ("refused", "Refused")],
        string="Offer Status",
        copy=False,
    )
    partner = fields.Many2one("res.partner", string="Partner", required=True)
    property = fields.Many2one(
        "estate.property", string="Property", required=True, readonly=True
    )
    property_type = fields.Many2one(related="property.property_type", store=True)

    validity = fields.Integer(string="Validity (in days)", default=7)
    date_deadline = fields.Date(
        string="Deadline",
        compute="_compute_validity_date",
        inverse="_inverse_validity_date",
        store=True,
    )

    @api.depends("validity")
    def _compute_validity_date(self):
        for offer in self:
            offer.date_deadline = datetime.now() + timedelta(days=offer.validity)

    def _inverse_validity_date(self):
        for offer in self:
            offer.validity = (offer.date_deadline - datetime.now().date()).days

    def action_offer_accept(self):
        total_offers = self.property.offers
        for offer in self:
            if any(total_offer.status == "accepted" for total_offer in total_offers):
                raise UserError("Two offers cannot  be accepted at the same time!")
            offer.status = "accepted"
            offer.property.buyer = offer.partner.id
            offer.property.selling_price = offer.offer_price
            offer.property.state = "offer_accepted"

    def action_offer_refuse(self):
        for offer in self:
            offer.status = "refused"

    @api.model_create_multi
    def create(self, vals):
        offer = (
            self.env["estate.property.offer"]
            .search([("property", "=", vals[0]["property"])])
            .mapped("offer_price")
        )
        if offer:
            max_offer = max(offer)
            if max_offer and vals[0]["offer_price"] < max_offer:
                raise ValidationError(
                    f"Cannot create offer with amount less than {int(max_offer)} :-("
                )
        res = super().create(vals)
        res.property.state = "offer_received"
        return res
