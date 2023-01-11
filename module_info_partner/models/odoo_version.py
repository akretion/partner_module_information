from odoo import fields, models


class OdooVersion(models.Model):
    _name = "odoo.version"
    _rec_name = "version"
    _description = "Odoo Version"

    version = fields.Selection(
        [
            ("6.1", "6.1"),
            ("7.0", "7.0"),
            ("8.0", "8.0"),
            ("9.0", "9.0"),
            ("10.0", "10.0"),
            ("11.0", "11.0"),
            ("12.0", "12.0"),
            ("13.0", "13.0"),
            ("14.0", "14.0"),
            ("15.0", "15.0"),
            ("16.0", "16.0"),
        ]
    )
