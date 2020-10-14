# Copyright 2020 Akretion (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging


from odoo.addons.base_rest.components.service import skip_secure_params
from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class GithubModuleService(Component):
    _inherit = "base.rest.service"
    _name = "github.module.service"
    _collection = "github.module"
    _usage = "module"

    #    def _validator_return_github_module_information(self):
    #        return {
    #       }

    @skip_secure_params
    def github_module_information(self):
        #        sync_fields = [
        #            'name',
        #            'technical_name',
        #            'description_rst',
        #            'description_rst_html',
        #            'author_ids_description',
        #            'organization_serie_ids',
        #        ]
        #        data = self.env["odoo.module"].search_read([], sync_fields)
        data = []
        modules = self.env["odoo.module"].search([])
        for module in modules:
            data.append(
                {
                    "name": module.name,
                    "technical_name": module.technical_name,
                    "description_rst": module.description_rst,
                    "description_rst_html": module.description_rst_html,
                    "author_ids_description": module.author_ids_description,
                    # remove duplicates
                    "versions": list(set(module.organization_serie_ids.mapped("name"))),
                }
            )
        return data
