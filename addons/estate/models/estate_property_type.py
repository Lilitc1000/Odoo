from odoo import fields, models, api
from collections import Counter


class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Estate Property Type Model"
    _order = "sequence"
    name = fields.Char(string="Name", required=True)
    sequence = fields.Integer(
        "Sequence",
    )
    properties = fields.One2many(
        "estate.property", "property_type", required=True, string="Properties"
    )
    offers = fields.One2many(
        "estate.property.offer", inverse_name="property_type", string="Offer ID"
    )

    _sql_constraints = {
        ("property_type_unique", "unique(name)", "The Proprty Type must be different!!")
    }

    offer_count = fields.Integer(
        compute="_compute_count_property", string="Offer Count"
    )

    @api.depends("offers")
    def _compute_count_property(self):
        for property_type in self:
            property_type.offer_count = Counter(property_type.offers)

    def action_stat_button(self):
        self.ensure_one()
        xml_id = self.env.context.get("xml_id")
        if xml_id:
            res = self.env["ir.actions.act_window"]._for_xml_id(xml_id)
            res.update(
                context=dict(
                    self.env.context, default_property_type=self.id, group_by=False
                ),
                domain=[("property_type", "=", self.id)],
            )
            return res
        return False
