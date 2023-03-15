from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    module_auth_api_key_id = fields.Many2one("auth.api.key", string="Module API KEY")
    version_id = fields.Many2one("odoo.version", string="Current Odoo version")
