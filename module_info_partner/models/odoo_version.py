from odoo import fields, models


class OdooVersion(models.Model):
    _name = "odoo.version"
    _rec_name = "version"
    _description = "Odoo Version"

    version = fields.Char()
