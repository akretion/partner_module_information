# coding: utf-8

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = "res.partner"

    module_auth_api_key_id = fields.Many2one("auth.api.key", string="Module API KEY")
