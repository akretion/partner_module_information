import requests_mock
import yaml
from mock import patch

from odoo.tests import TransactionCase


@patch("odoo.addons.module_info_import.models.module_information.VERSIONS", ["14.0"])
class TestinfoImport(TransactionCase):
    def setUp(self):
        super().setUp()
        self.modules_yaml = self.env["module.information"].get_module_info("14.0")
        with open("tests/data/module_list_14.yaml", "r") as f:
            self.modules_yaml = f.read()

    def test_modules_import(self):
        with requests_mock.mock() as m:
            m.get(
                "https://raw.githubusercontent.com/akretion/"
                "odoo-module-tracker/gh-pages/14.0.yml",
                text=self.modules_yaml,
            )

            self.env["module.information"].synchronize_module()

            modules_dict = yaml.safe_load(self.modules_yaml)

            module_list = []
            for _orga, repos in modules_dict.items():
                for _repo, modules in repos.items():
                    for module in modules:
                        if module not in module_list:
                            module_list.append(module)

            self.assertEqual(
                len(module_list),
                self.env["module.information"].search_count(
                    [("available_version_ids", "=", "14.0")]
                ),
            )

    def test_modules_import_duplicate(self):
        with open("tests/data/module_list_14_duplicate.yaml", "r") as f:
            self.modules_yaml = f.read()
            with requests_mock.mock() as m:
                m.get(
                    "https://raw.githubusercontent.com/akretion/"
                    "odoo-module-tracker/gh-pages/14.0.yml",
                    text=self.modules_yaml,
                )

                self.env["module.information"].synchronize_module()
                module = self.env["module.information"].search(
                    [("technical_name", "=", "single_module_test")]
                )
                # test module single is imported
                self.assertEqual(module.host_repository_id.organisation, "tiers")
                # test module duplicate
                module = self.env["module.information"].search(
                    [("technical_name", "=", "duplicate_module_test1")]
                )
                # check priority to OCA
                self.assertEqual(module.host_repository_id.organisation, "oca")
                # test duplicate module diffrent order
                module = self.env["module.information"].search(
                    [("technical_name", "=", "duplicate_module_test2")]
                )
                # check priority to OCA
                self.assertEqual(module.host_repository_id.organisation, "oca")
