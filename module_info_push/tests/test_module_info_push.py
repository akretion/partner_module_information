import requests_mock

from odoo.tests import TransactionCase


class Testinfopush(TransactionCase):
    def setUp(self):
        super().setUp()
        self.env["ir.config_parameter"].sudo().set_param(
            "module.api.url", "https://master.odoopushtest.com"
        )
        self.env["ir.config_parameter"].sudo().set_param("module.push.custom", False)

    def test_push_installed_modules_info(self):
        with requests_mock.mock() as m:
            m.post(
                "https://master.odoopushtest.com/module-api"
                "/module/synchronize_installed_module_info",
                text='{"id": "432161"}',
            )
            self.env["ir.module.module"].push_installed_module_info()
            data = m.request_history[0].json()
            self.assertEqual(
                len(data["modules_info"]["modules"]),
                self.env["ir.module.module"].search_count(
                    [("state", "in", ("installed", "to upgrade"))]
                ),
            )
