# coding: utf-8

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    target_odoo_version_id = fields.Many2one("odoo.version", string="Target version")
