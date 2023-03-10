from odoo import fields, models


class OdooVersion(models.Model):
    _name = "odoo.version"
    _rec_name = "name"
    _description = "Odoo Version"

    name = fields.Char()
