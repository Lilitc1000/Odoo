from odoo import fields, models


class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Estate Property Tag Model"
    _order = "name"
    name = fields.Char(string="Name", required=True)
    color = fields.Integer("Color")

    _sql_constraints = {
        ("property_tag_unique", "unique(name)", "The Proprty Tag must be different!!")
    }
