from odoo import fields, models


class HostRepository(models.Model):
    _inherit = "host.repository"

    updated_at = fields.Datetime(string="Last Update")
