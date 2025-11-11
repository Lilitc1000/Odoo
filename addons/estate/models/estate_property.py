from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Estate property Model"
    _order = "id desc"

    name = fields.Char(required=True, string="Name")
    description = fields.Text(string="Description")
    postcode = fields.Char(string="Postal Code")
    date_availability = fields.Date(
        copy=False,
        default=fields.Date.add(fields.Date.today(), months=3),
        string="Available From",
    )
    expected_price = fields.Float(required=True, string="Expected Price")
    selling_price = fields.Float(readonly=True, copy=False, string="Selling Price")
    bedrooms = fields.Integer(default=2, string="Bedrooms")
    living_area = fields.Integer(string="Living Area")
    facades = fields.Integer(string="Facades")
    garage = fields.Boolean(string="Garage")
    garden = fields.Boolean(string="Garden")
    garden_area = fields.Integer(string="Garden Area")
    garden_orientation = fields.Selection(
        selection=[
            ("north", "North"),
            ("south", "South"),
            ("east", "East"),
            ("west", "West"),
        ],
        string="Orientation",
    )
    state = fields.Selection(
        selection=[
            ("new", "New"),
            ("offer_received", "Offer Recieved"),
            ("offer_accepted", "Offer Accepted"),
            ("sold", "Sold"),
            ("cancel", "Canceled"),
        ],
        default="new",
        string="Status",
    )
    active = fields.Boolean(default=True, string="Active")

    buyer = fields.Many2one("res.partner", readonly=True, copy=False, string="Buyer")
    seller = fields.Many2one("res.users", string="Seller")
    property_type = fields.Many2one("estate.property.type", string="Property Type")

    tags = fields.Many2many("estate.property.tag", string="Tags")

    offers = fields.One2many("estate.property.offer", "property")

    total_area = fields.Float(string="Total Area", compute="_compute_total_area")
    best_price = fields.Float(string="Best Offer", compute="_compute_best_price")

    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for property in self:
            property.total_area = property.living_area + property.garden_area

    @api.depends("offers.offer_price")
    def _compute_best_price(self):
        for property in self:
            if property.offers:
                property.best_price = max(property.offers.mapped("offer_price"))
            else:
                property.best_price = 0

    @api.onchange("garden")
    def _onchange_garden(self):
        for property in self:
            if property.garden:
                property.garden_area = 10
                property.garden_orientation = "north"
            else:
                property.garden_area = 0
                property.garden_orientation = ""

    def action_sold_property(self):
        for property in self:
            if property.state == "cancel":
                raise UserError("You cannot sell Cancelled Property")
            elif not any(offer.status == "accepted" for offer in self.offers):
                raise UserError("You cannot sell property which has no accepted offer")
            else:
                property.state = "sold"
                return True

    def action_cancel_property(self):
        for property in self:
            if property.state == "sold":
                raise UserError("You cannot cancel Sold Property")
            else:
                property.state = "cancel"
                return True

    _sql_constraints = {
        (
            "check_expected_price",
            "CHECK(expected_price >= 0)",
            "The expected price cannot be less than 0!!",
        ),
        (
            "check_selling_price",
            "CHECK(selling_price >= 0)",
            "The selling price cannot be less than 0!!",
        ),
    }

    @api.constrains("selling_price", "expected_price")
    def _check_selling_price(self):
        for property in self:
            if property.selling_price:
                minimun_value = property.expected_price * 0.9
                if minimun_value > property.selling_price:
                    raise ValidationError(
                        "The offer value must be greater than 90% of Expected Price!!"
                    )

    @api.ondelete(at_uninstall=False)
    def _unlink_if_not_new_or_canceled(self):
        if any(
            property.state != "new" and property.state != "cancel" for property in self
        ):
            raise UserError("You can only delete new or cancelled property!!")
