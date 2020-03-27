# -*- coding: utf-8 -*-
# Copyright 2020 Akretion (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.addons.base_rest.controllers import main


class GithubModuleController(main.RestController):
    _root_path = "/github_module_api/"
    _collection_name = "github.module"
    _default_auth = "public"
